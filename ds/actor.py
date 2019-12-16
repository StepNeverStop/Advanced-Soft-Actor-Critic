import functools
import importlib
import logging
import logging.handlers
from pathlib import Path
from queue import Queue
import sys
import threading
import time
import yaml

import numpy as np
import tensorflow as tf
import grpc

from .proto import replay_pb2, replay_pb2_grpc
from .proto import learner_pb2, learner_pb2_grpc
from .proto.ndarray_pb2 import Empty
from .proto.numproto import ndarray_to_proto, proto_to_ndarray
from .proto.pingpong_pb2 import Ping, Pong

from .sac_ds_base import SAC_DS_Base

from mlagents.envs.environment import UnityEnvironment
from algorithm.trans_cache import TransCache
import algorithm.config_helper as config_helper
from algorithm.agent import Agent


class Actor(object):
    train_mode = True
    _websocket_connected = False
    _agent_class = Agent

    def __init__(self, config_path, args):
        self.config_path = config_path
        self.config, net_config, self.reset_config = self._init_config(self.config_path, args)

        self._init_env(net_config)
        self._trans_cache = TransCache(self.config['add_trans_batch'])
        self._run()

    def _init_config(self, config_path, args):
        config_file_path = f'{config_path}/{args.config}' if args.config is not None else None
        config = config_helper.initialize_config_from_yaml(f'{Path(__file__).resolve().parent}/default_config.yaml',
                                                           config_file_path)

        # initialize config from command line arguments
        self.train_mode = not args.run
        self.run_in_editor = args.editor

        if args.build_port is not None:
            config['base_config']['build_port'] = args.build_port
        if args.seed is not None:
            config['sac_config']['seed'] = args.seed
        if args.sac is not None:
            config['base_config']['sac'] = args.sac
        if args.agents is not None:
            config['reset_config']['copy'] = args.agents

        self.logger = config_helper.set_logger('ds.actor', args.logger_file)

        config_helper.display_config(config, self.logger)

        return config['base_config'], config['net_config'], config['reset_config']

    def _init_env(self, net_config):
        self._stub = StubController(net_config)

        if self.run_in_editor:
            self.env = UnityEnvironment(base_port=5004)
        else:
            self.env = UnityEnvironment(file_name=self.config['build_path'],
                                        no_graphics=self.train_mode,
                                        base_port=self.config['build_port'],
                                        args=['--scene', self.config['scene']])

        self.env.reset()
        self.default_brain_name = self.env.external_brain_names[0]

        self.logger.info(f'{self.config["build_path"]} initialized')

    def _init_sac(self):
        brain_params = self.env.brains[self.default_brain_name]
        state_dim = brain_params.vector_observation_space_size
        action_dim = brain_params.vector_action_space_size[0]

        custom_sac_model = importlib.import_module(f'{self.config_path.replace("/",".")}.{self.config["sac"]}')

        self.sac_actor = SAC_DS_Base(state_dim=state_dim,
                                     action_dim=action_dim,
                                     model_root_path=None,
                                     model=custom_sac_model,
                                     train_mode=False,

                                     burn_in_step=self.config['burn_in_step'],
                                     n_step=self.config['n_step'],
                                     use_rnn=self.config['use_rnn'],
                                     use_prediction=self.config['use_prediction'])

        self.logger.info(f'sac_actor initialized')

    def _update_policy_variables(self):
        variables = self._stub.update_policy_variables()
        if variables is not None:
            self.sac_actor.update_policy_variables(variables)

    def _add_trans(self, *trans):
        # n_states, n_actions, n_rewards, state_, done, rnn_state
        self._trans_cache.add(*trans)

        trans = self._trans_cache.get_batch_trans()
        if trans is not None:
            if self.config['use_rnn']:
                n_states, n_actions, n_rewards, state_, done, rnn_state = trans
                mu_n_probs = self.sac_actor.get_rnn_n_step_probs(n_states, n_actions, rnn_state).numpy()
                self._stub.add_transitions(n_states, n_actions, n_rewards, state_, done, mu_n_probs, rnn_state)
            else:
                n_states, n_actions, n_rewards, state_, done = trans
                mu_n_probs = self.sac_actor.get_n_step_probs(n_states, n_actions).numpy()
                self._stub.add_transitions(n_states, n_actions, n_rewards, state_, done, mu_n_probs)

    def _run(self):
        iteration = 0

        while True:
            # replay or learner is offline, waiting...
            if not self._stub.connected:
                iteration = 0
                self.logger.warning('waiting for connection')
                time.sleep(2)
                continue

            # learner is online, reset all settings
            if iteration == 0 and self._stub.connected:
                self._trans_cache.clear()
                self._init_sac()

                brain_info = self.env.reset(train_mode=self.train_mode, config=self.reset_config)[self.default_brain_name]
                if self.config['use_rnn']:
                    initial_rnn_state = self.sac_actor.get_initial_rnn_state(len(brain_info.agents))
                    rnn_state = initial_rnn_state

            if self.config['reset_on_iteration']:
                brain_info = self.env.reset(train_mode=self.train_mode)[self.default_brain_name]
                if self.config['use_rnn']:
                    rnn_state = initial_rnn_state

            agents = [self._agent_class(i,
                                        tran_len=self.config['burn_in_step'] + self.config['n_step'],
                                        stagger=self.config['stagger'],
                                        use_rnn=self.config['use_rnn'])
                      for i in brain_info.agents]

            states = brain_info.vector_observations
            step = 0

            if self.config['update_policy_variables_per_step'] == -1:
                self._update_policy_variables()

            while False in [a.done for a in agents] and self._stub.connected:
                if self.config['update_policy_variables_per_step'] != -1 and step % self.config['update_policy_variables_per_step'] == 0:
                    self._update_policy_variables()

                if self.config['use_rnn']:
                    actions, next_rnn_state = self.sac_actor.choose_rnn_action(states.astype(np.float32),
                                                                               rnn_state)
                    next_rnn_state = next_rnn_state.numpy()
                else:
                    actions = self.sac_actor.choose_action(states.astype(np.float32))

                actions = actions.numpy()

                brain_info = self.env.step({
                    self.default_brain_name: actions
                })[self.default_brain_name]

                states_ = brain_info.vector_observations
                if step == self.config['max_step']:
                    brain_info.local_done = [True] * len(brain_info.agents)
                    brain_info.max_reached = [True] * len(brain_info.agents)

                tmp_results = [agents[i].add_transition(states[i],
                                                        actions[i],
                                                        brain_info.rewards[i],
                                                        brain_info.local_done[i],
                                                        brain_info.max_reached[i],
                                                        states_[i],
                                                        rnn_state[i] if self.config['use_rnn'] else None)
                               for i in range(len(agents))]

                trans_list, episode_trans_list = zip(*tmp_results)

                trans_list = [t for t in trans_list if t is not None]
                if len(trans_list) != 0:
                    # n_states, n_actions, n_rewards, state_, done, rnn_state
                    trans = [np.concatenate(t, axis=0) for t in zip(*trans_list)]
                    self._add_trans(*trans)

                if self.config['use_rnn'] and self.config['use_prediction']:
                    episode_trans_list = [t for t in episode_trans_list if t is not None]
                    if len(episode_trans_list) != 0:
                        # n_states, n_actions, n_rewards, done, rnn_state
                        for episode_trans in episode_trans_list:
                            self._stub.add_episode_trans(*episode_trans)

                states = states_
                if self.config['use_rnn']:
                    rnn_state = next_rnn_state
                    rnn_state[brain_info.local_done] = initial_rnn_state[brain_info.local_done]

                step += 1

            self._log_episode_info(iteration, agents)
            iteration += 1

    def _log_episode_info(self, iteration, agents):
        rewards = [a.reward for a in agents]
        rewards_sorted = ", ".join([f"{i:.1f}" for i in sorted(rewards)])
        self.logger.info(f'{iteration}, rewards {rewards_sorted}')


class StubController:
    def __init__(self, net_config):
        self._replay_channel = grpc.insecure_channel(f'{net_config["replay_host"]}:{net_config["replay_port"]}',
                                                     [('grpc.max_reconnect_backoff_ms', 5000)])
        self._replay_stub = replay_pb2_grpc.ReplayServiceStub(self._replay_channel)

        self._learner_channel = grpc.insecure_channel(f'{net_config["learner_host"]}:{net_config["learner_port"]}',
                                                      [('grpc.max_reconnect_backoff_ms', 5000)])
        self._learner_stub = learner_pb2_grpc.LearnerServiceStub(self._learner_channel)

        self._replay_connected = False
        self._learner_connected = False
        self._logger = logging.getLogger('ds.actor.stub')

        t_replay = threading.Thread(target=self._start_replay_persistence)
        t_replay.start()
        t_learner = threading.Thread(target=self._start_learner_persistence)
        t_learner.start()

    @property
    def connected(self):
        return self._replay_connected and self._learner_connected

    def add_transitions(self, *transitions):
        try:
            self._replay_stub.Add(replay_pb2.AddRequest(transitions=[ndarray_to_proto(t)
                                                                     for t in transitions]))
        except grpc.RpcError:
            self._logger.error('connection lost in "add_transitions"')

    def add_episode_trans(self, *transitions):
        try:
            self._replay_stub.AddEpisode(replay_pb2.AddEpisodeRequest(transitions=[ndarray_to_proto(t)
                                                                                   for t in transitions]))
        except grpc.RpcError:
            self._logger.error('connection lost in "add_episode_trans"')

    def update_policy_variables(self):
        try:
            response = self._learner_stub.GetPolicyVariables(Empty())
            return [proto_to_ndarray(v) for v in response.variables]
        except grpc.RpcError:
            self._logger.error('connection lost in "update_policy_variables"')


    def _start_replay_persistence(self):
        def request_messages():
            while True:
                yield Ping(time=int(time.time() * 1000))
                time.sleep(5)
                if not self._replay_connected:
                    break

        while True:
            try:
                reponse_iterator = self._replay_stub.Persistence(request_messages())
                for response in reponse_iterator:
                    if not self._replay_connected:
                        self._replay_connected = True
                        self._logger.info('replay connected')
            except grpc.RpcError:
                if self._replay_connected:
                    self._replay_connected = False
                    self._logger.error('replay disconnected')
            finally:
                time.sleep(2)

    def _start_learner_persistence(self):
        def request_messages():
            while True:
                yield Ping(time=int(time.time() * 1000))
                time.sleep(5)
                if not self._learner_connected:
                    break

        while True:
            try:
                reponse_iterator = self._learner_stub.Persistence(request_messages())
                for response in reponse_iterator:
                    if not self._learner_connected:
                        self._learner_connected = True
                        self._logger.info('learner connected')
            except grpc.RpcError:
                if self._learner_connected:
                    self._learner_connected = False
                    self._logger.error('learner disconnected')
            finally:
                time.sleep(2)
