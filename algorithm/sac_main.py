from collections import deque
from pathlib import Path
import functools
import getopt
import importlib
import logging
import logging.handlers
import os
import random
import shutil
import string
import sys
import time
import yaml

import numpy as np

from .sac_base import SAC_Base
from .agent import Agent

import algorithm.config_helper as config_helper


class Main(object):
    train_mode = True
    _agent_class = Agent  # For different environments

    def __init__(self, config_path, args):
        """
        config_path: the directory of config file
        args: command arguments generated by argparse
        """
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
        config_file_path = f'{config_path}/config.yaml'
        # Merge default_config.yaml and custom config.yaml
        config = config_helper.initialize_config_from_yaml(f'{Path(__file__).resolve().parent}/default_config.yaml',
                                                           config_file_path,
                                                           args.config)

        # Initialize config from command line arguments
        self.train_mode = not args.run
        self.last_ckpt = args.ckpt
        self.render = args.render
        self.run_in_editor = args.editor

        if args.name is not None:
            config['base_config']['name'] = args.name
        if args.port is not None:
            config['base_config']['port'] = args.port
        if args.sac is not None:
            config['base_config']['sac'] = args.sac
        if args.agents is not None:
            config['base_config']['n_agents'] = args.agents

        # Replace {time} from current time and random letters
        rand = ''.join(random.sample(string.ascii_letters, 4))
        config['base_config']['name'] = config['base_config']['name'].replace('{time}', self._now + rand)
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
        if self.config['env_type'] == 'UNITY':
            from algorithm.env_wrapper.unity_wrapper import UnityWrapper

            if self.run_in_editor:
                self.env = UnityWrapper(train_mode=self.train_mode, base_port=5004)
            else:
                self.env = UnityWrapper(train_mode=self.train_mode,
                                        file_name=self.config['build_path'][sys.platform],
                                        base_port=self.config['port'],
                                        scene=self.config['scene'],
                                        n_agents=self.config['n_agents'])

        elif self.config['env_type'] == 'GYM':
            from algorithm.env_wrapper.gym_wrapper import GymWrapper

            self.env = GymWrapper(train_mode=self.train_mode,
                                  env_name=self.config['build_path'],
                                  render=self.render,
                                  n_agents=self.config['n_agents'])
        else:
            raise RuntimeError(f'Undefined Environment Type: {self.config["env_type"]}')

        self.obs_dims, self.action_dim, is_discrete = self.env.init()

        # If model exists, load saved model, or copy a new one
        if os.path.isfile(f'{model_root_path}/sac_model.py'):
            custom_sac_model = importlib.import_module(f'{model_root_path.replace("/",".")}.sac_model')
        else:
            custom_sac_model = importlib.import_module(f'{config_path.replace("/",".")}.{self.config["sac"]}')
            shutil.copyfile(f'{config_path}/{self.config["sac"]}.py', f'{model_root_path}/sac_model.py')

        self.sac = SAC_Base(obs_dims=self.obs_dims,
                            action_dim=self.action_dim,
                            is_discrete=is_discrete,
                            model_root_path=model_root_path,
                            model=custom_sac_model,
                            train_mode=self.train_mode,
                            last_ckpt=self.last_ckpt,

                            replay_config=replay_config,

                            **sac_config)

    def _run(self):
        use_rnn = self.sac.use_rnn

        obs_list = self.env.reset(reset_config=self.reset_config)

        agents = [self._agent_class(i, use_rnn=self.sac.use_rnn)
                  for i in range(self.config['n_agents'])]

        if use_rnn:
            initial_rnn_state = self.sac.get_initial_rnn_state(len(agents))
            rnn_state = initial_rnn_state

        is_max_reached = False

        for iteration in range(self.config['max_iter'] + 1):
            if self.config['reset_on_iteration'] or is_max_reached:
                obs_list = self.env.reset(reset_config=self.reset_config)
                for agent in agents:
                    agent.clear()

                if use_rnn:
                    rnn_state = initial_rnn_state
            else:
                for agent in agents:
                    agent.reset()

            is_max_reached = False
            action = np.zeros([len(agents), self.action_dim], dtype=np.float32)
            step = 0

            while False in [a.done for a in agents]:
                if use_rnn:
                    # burn-in padding
                    for agent in [a for a in agents if a.is_empty()]:
                        for _ in range(self.sac.burn_in_step):
                            agent.add_transition([np.zeros(t) for t in self.obs_dims],
                                                 np.zeros(self.action_dim),
                                                 0, False, False,
                                                 [np.zeros(t) for t in self.obs_dims],
                                                 initial_rnn_state[0])

                    action, next_rnn_state = self.sac.choose_rnn_action([o.astype(np.float32) for o in obs_list],
                                                                        action,
                                                                        rnn_state)
                    next_rnn_state = next_rnn_state.numpy()
                else:
                    action = self.sac.choose_action([o.astype(np.float32) for o in obs_list])

                action = action.numpy()

                next_obs_list, reward, local_done, max_reached = self.env.step(action)

                if step == self.config['max_step']:
                    local_done = [True] * len(agents)
                    max_reached = [True] * len(agents)
                    is_max_reached = True

                episode_trans_list = [agents[i].add_transition([o[i] for o in obs_list],
                                                               action[i],
                                                               reward[i],
                                                               local_done[i],
                                                               max_reached[i],
                                                               [o[i] for o in next_obs_list],
                                                               rnn_state[i] if use_rnn else None)
                                      for i in range(len(agents))]

                if self.train_mode:
                    episode_trans_list = [t for t in episode_trans_list if t is not None]
                    if len(episode_trans_list) != 0:
                        # n_obses_list, n_actions, n_rewards, next_obs_list, n_dones,
                        # n_rnn_states
                        for episode_trans in episode_trans_list:
                            self.sac.fill_replay_buffer(*episode_trans)
                    self.sac.train()

                obs_list = next_obs_list
                action[local_done] = np.zeros(self.action_dim)
                if use_rnn:
                    rnn_state = next_rnn_state
                    rnn_state[local_done] = initial_rnn_state[local_done]

                step += 1

            if self.train_mode:
                self._log_episode_summaries(iteration, agents)

            self._log_episode_info(iteration, agents)

        self.sac.save_model()
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
        rewards = ", ".join([f"{i:6.1f}" for i in rewards])
        self.logger.info(f'{iteration}, rewards {rewards}')
