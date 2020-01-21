from collections import deque
from pathlib import Path
import functools
import getopt
import importlib
import logging
import logging.handlers
import os
import shutil
import sys
import time
import yaml

import numpy as np
import tensorflow as tf

from .sac_base import SAC_Base
from .agent import Agent

import algorithm.config_helper as config_helper
from algorithm.env_wrapper import EnvWrapper


class Main(object):
    train_mode = True
    _agent_class = Agent

    def __init__(self, config_path, args):
        self._now = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))

        (self.config, self.reset_config,
         replay_config,
         sac_config,
         model_root_path) = self._init_config(config_path, args)
        self._init_env(model_root_path, config_path,
                       sac_config,
                       replay_config)
        self._run()

    def _init_config(self, config_path, args):
        config_file_path = f'{config_path}/{args.config}' if args.config is not None else None
        config = config_helper.initialize_config_from_yaml(f'{Path(__file__).resolve().parent}/default_config.yaml',
                                                           config_file_path)

        # initialize config from command line arguments
        self.train_mode = not args.run
        self.render = args.render
        self.run_in_editor = args.editor

        if args.name is not None:
            config['base_config']['name'] = args.name
        if args.port is not None:
            config['base_config']['port'] = args.port
        if args.seed is not None:
            config['sac_config']['seed'] = args.seed
        if args.sac is not None:
            config['base_config']['sac'] = args.sac
        if args.agents is not None:
            config['reset_config']['copy'] = args.agents

        config['base_config']['name'] = config['base_config']['name'].replace('{time}', self._now)
        model_root_path = f'models/{config["base_config"]["scene"]}/{config["base_config"]["name"]}'

        logger_file = f'{model_root_path}/{args.logger_file}' if args.logger_file is not None else None
        self.logger = config_helper.set_logger('sac', logger_file)

        if self.train_mode:
            config_helper.save_config(config, model_root_path, 'config.yaml')

        config_helper.display_config(config, self.logger)

        return (config['base_config'],
                config['reset_config'],
                config['replay_config'],
                config['sac_config'],
                model_root_path)

    def _init_env(self, model_root_path, config_path,
                  sac_config,
                  replay_config):
        if self.run_in_editor:
            self.env = EnvWrapper(train_mode=self.train_mode, base_port=5004)
        else:
            self.env = EnvWrapper(train_mode=self.train_mode,
                                  file_name=self.config['build_path'],
                                  no_graphics=not self.render and self.train_mode,
                                  base_port=self.config['port'],
                                  args=['--scene', self.config['scene']])

        self.state_dim, self.action_dim = self.env.init()

        # if model exists, load saved model, else, copy a new one
        if os.path.isfile(f'{model_root_path}/sac_model.py'):
            custom_sac_model = importlib.import_module(f'{model_root_path.replace("/",".")}.sac_model')
        else:
            custom_sac_model = importlib.import_module(f'{config_path.replace("/",".")}.{self.config["sac"]}')
            shutil.copyfile(f'{config_path}/{self.config["sac"]}.py', f'{model_root_path}/sac_model.py')

        self.sac = SAC_Base(state_dim=self.state_dim,
                            action_dim=self.action_dim,
                            model_root_path=model_root_path,
                            model=custom_sac_model,
                            train_mode=self.train_mode,

                            burn_in_step=self.config['burn_in_step'],
                            n_step=self.config['n_step'],
                            use_rnn=self.config['use_rnn'],
                            use_prediction=self.config['use_prediction'],

                            replay_config=replay_config,

                            **sac_config)

    def _run(self):
        agent_ids, state = self.env.reset(reset_config=self.reset_config)

        agents = [self._agent_class(i,
                                    tran_len=self.config['burn_in_step'] + self.config['n_step'],
                                    stagger=self.config['stagger'],
                                    use_rnn=self.config['use_rnn'])
                  for i in agent_ids]

        if self.config['use_rnn']:
            initial_rnn_state = self.sac.get_initial_rnn_state(len(agents))
            rnn_state = initial_rnn_state

        for iteration in range(self.config['max_iter'] + 1):
            if self.config['reset_on_iteration']:
                _, state = self.env.reset(reset_config=self.reset_config)
                for agent in agents:
                    agent.clear()

                if self.config['use_rnn']:
                    rnn_state = initial_rnn_state
            else:
                for agent in agents:
                    agent.reset()
            """
            s0    s1    s2    s3    s4    s5    s6
             └──burn_in_step───┘     └───n_step──┘
             └───────────deque_maxlen────────────┘
                         s2    s3    s4    s5    s6    s7    s8
             └─────┘
             stagger
            """

            # burn in padding
            if self.config['use_rnn']:
                for agent in agents:
                    if agent.is_empty():
                        for _ in range(self.config['burn_in_step']):
                            agent.add_transition(np.zeros(self.state_dim),
                                                 np.zeros(self.action_dim),
                                                 0, False, False,
                                                 np.zeros(self.state_dim),
                                                 initial_rnn_state[0])

            step = 0

            while False in [a.done for a in agents]:
                if self.config['use_rnn']:
                    action, next_rnn_state = self.sac.choose_rnn_action(state.astype(np.float32),
                                                                        rnn_state)
                    next_rnn_state = next_rnn_state.numpy()
                else:
                    action = self.sac.choose_action(state.astype(np.float32))

                action = action.numpy()

                state_, reward, local_done, max_reached = self.env.step(action)

                if step == self.config['max_step']:
                    local_done = [True] * len(agents)
                    max_reached = [True] * len(agents)

                tmp_results = [agents[i].add_transition(state[i],
                                                        action[i],
                                                        reward[i],
                                                        local_done[i],
                                                        max_reached[i],
                                                        state_[i],
                                                        rnn_state[i] if self.config['use_rnn'] else None)
                               for i in range(len(agents))]

                if self.train_mode:
                    trans_list, ep_rewards_list = zip(*tmp_results)

                    trans_list = [t for t in trans_list if t is not None]
                    ep_rewards_list = [t for t in ep_rewards_list if t is not None]
                    if len(trans_list) != 0:
                        # n_states, n_actions, n_rewards, done, rnn_state
                        trans = [np.concatenate(t, axis=0) for t in zip(*trans_list)]

                        if len(ep_rewards_list) != 0:
                            self.sac.fill_replay_buffer(*trans, ep_rewards_list=ep_rewards_list)
                        else:
                            self.sac.fill_replay_buffer(*trans)

                    # episode_trans_list = [t for t in episode_trans_list if t is not None]
                    # if len(episode_trans_list) != 0:
                    #     # n_states, n_actions, n_rewards, state_, n_dones, rnn_state
                    #     for episode_trans in episode_trans_list:
                    #         self.sac.fill_replay_buffer(*episode_trans)
                    self.sac.train()

                state = state_
                if self.config['use_rnn']:
                    rnn_state = next_rnn_state
                    rnn_state[local_done] = initial_rnn_state[local_done]

                step += 1

            if self.train_mode:
                self._log_episode_summaries(iteration, agents)

                if iteration % self.config['save_model_per_iter'] == 0:
                    self.sac.save_model(iteration)

            self._log_episode_info(iteration, agents)

        self.env.close()

    def _log_episode_summaries(self, iteration, agents):
        rewards = np.array([a.reward for a in agents])
        self.sac.write_constant_summaries([
            {'tag': 'reward/mean', 'simple_value': rewards.mean()},
            {'tag': 'reward/max', 'simple_value': rewards.max()},
            {'tag': 'reward/min', 'simple_value': rewards.min()}
        ], iteration)

    def _log_episode_info(self, iteration, agents):
        rewards = [a.reward for a in agents]
        rewards_sorted = ", ".join([f"{i:.1f}" for i in sorted(rewards)])
        self.logger.info(f'iter {iteration}, rewards {rewards_sorted}')
