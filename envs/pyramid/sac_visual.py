import numpy as np
import tensorflow as tf
import tensorflow_probability as tfp

from algorithm.common_models import ModelTransition, ModelRNNRep


class ModelTransition(ModelTransition):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.seq = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation=tf.nn.tanh),
            tf.keras.layers.Dense(128, activation=tf.nn.relu),
            tf.keras.layers.Dense(128, activation=tf.nn.relu),
            tf.keras.layers.Dense(state_dim + state_dim)
        ])

        self.next_state_tfpd = tfp.layers.DistributionLambda(make_distribution_fn=lambda t: tfp.distributions.Normal(t[0], t[1]))

        self(tf.keras.Input(shape=(state_dim + 2,)), tf.keras.Input(shape=(action_dim,)))

    def call(self, state, action):
        next_state = self.seq(tf.concat([state, action], -1))
        mean, logstd = tf.split(next_state, num_or_size_splits=2, axis=-1)
        next_state_dist = self.next_state_tfpd([mean, tf.exp(logstd)])

        return next_state_dist

    def extra_obs(self, obs_list):
        return obs_list[1][..., -2:]


class ModelReward(tf.keras.Model):
    def __init__(self, state_dim):
        super().__init__()
        self.seq = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation=tf.nn.relu),
            tf.keras.layers.Dense(128, activation=tf.nn.relu),
            tf.keras.layers.Dense(1)
        ])

        self(tf.keras.Input(shape=(state_dim,)))

    def call(self, state):
        reward = self.seq(state)

        return reward


class ModelObservation(tf.keras.Model):
    def __init__(self, state_dim, obs_dims):
        super().__init__()
        assert obs_dims[0] == (84, 84, 3)
        assert obs_dims[1] == (6, )  # Only first 4

        self.vis_seq = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation=tf.nn.relu),
            tf.keras.layers.Dense(7 * 7 * 64, activation=tf.nn.relu),
            tf.keras.layers.Reshape(target_shape=(7, 7, 64)),
            tf.keras.layers.Conv2DTranspose(filters=64, kernel_size=3, strides=1, activation=tf.nn.relu),
            tf.keras.layers.Conv2DTranspose(filters=64, kernel_size=4, strides=2, activation=tf.nn.relu),
            tf.keras.layers.Conv2DTranspose(filters=3, kernel_size=8, strides=4),
        ])
        self.vec_seq = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation=tf.nn.relu),
            tf.keras.layers.Dense(128, activation=tf.nn.relu),
            tf.keras.layers.Dense(4)
        ])

        self(tf.keras.Input(shape=(state_dim,)))

    def call(self, state):
        batch = tf.shape(state)[0]
        t_state = tf.reshape(state, [-1, state.shape[-1]])
        vis_obs = self.vis_seq(t_state)
        vis_obs = tf.reshape(vis_obs, [batch, -1, *vis_obs.shape[1:]])

        vec_obs = self.vec_seq(state)

        return vis_obs, vec_obs

    def get_loss(self, state, obs_list):
        vis_obs, vec_obs = obs_list
        vec_obs = vec_obs[..., :-2]
        approx_vis_obs, approx_vec_obs = self(state)

        mse = tf.keras.losses.MeanSquaredError()

        return 0.5 * mse(approx_vis_obs, vis_obs) + 0.5 * mse(approx_vec_obs, vec_obs)


class ModelRep(ModelRNNRep):
    def __init__(self, obs_dims, action_dim):
        assert obs_dims[0] == (84, 84, 3)
        assert obs_dims[1] == (6, )  # Only first 4

        super().__init__(obs_dims, action_dim)
        self.conv = tf.keras.Sequential([
            tf.keras.layers.Conv2D(filters=32, kernel_size=8, strides=4, activation=tf.nn.relu),
            tf.keras.layers.Conv2D(filters=64, kernel_size=4, strides=2, activation=tf.nn.relu),
            tf.keras.layers.Conv2D(filters=64, kernel_size=3, strides=1, activation=tf.nn.relu),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(128, activation=tf.nn.relu),
            tf.keras.layers.Dense(64, activation=tf.nn.relu)
        ])

        self.rnn_units = 64
        self.layer_rnn = tf.keras.layers.GRU(self.rnn_units, return_sequences=True, return_state=True)
        self.seq = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation=tf.nn.tanh)
        ])

        self.get_call_result_tensors()

    def call(self, obs_list, pre_action, rnn_state):
        vis_obs, vec_obs = obs_list
        vec_obs = vec_obs[..., :-2]

        obs = tf.concat([vec_obs, pre_action], axis=-1)
        outputs, next_rnn_state = self.layer_rnn(obs, initial_state=rnn_state)

        batch = tf.shape(vis_obs)[0]
        vis_obs = tf.reshape(vis_obs, [-1, *vis_obs.shape[2:]])
        vis_obs = self.conv(vis_obs)
        vis_obs = tf.reshape(vis_obs, [batch, -1, vis_obs.shape[-1]])
        state = self.seq(tf.concat([vis_obs, outputs], axis=-1))

        return state, next_rnn_state, outputs


class ModelQ(tf.keras.Model):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.layer_state = tf.keras.layers.Dense(128, activation=tf.nn.relu)
        self.layer_action = tf.keras.layers.Dense(128, activation=tf.nn.relu)

        self.seq = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation=tf.nn.relu),
            tf.keras.layers.Dense(128, activation=tf.nn.relu),
            tf.keras.layers.Dense(128, activation=tf.nn.relu),
            tf.keras.layers.Dense(1)
        ])

        self(tf.keras.Input(shape=(state_dim,)), tf.keras.Input(shape=(action_dim,)))

    def call(self, state, action):
        state = self.layer_state(state)
        action = self.layer_action(action)
        l = tf.concat([state, action], -1)

        q = self.seq(l)
        return q


class ModelPolicy(tf.keras.Model):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.common_model = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation=tf.nn.relu),
            tf.keras.layers.Dense(128, activation=tf.nn.relu)
        ])
        self.mean_model = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation=tf.nn.relu),
            tf.keras.layers.Dense(action_dim)
        ])
        self.logstd_model = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation=tf.nn.relu),
            tf.keras.layers.Dense(action_dim)
        ])

        self.tfpd = tfp.layers.DistributionLambda(make_distribution_fn=lambda t: tfp.distributions.Normal(t[0], t[1]))

        self(tf.keras.Input(shape=(state_dim,)))

    def call(self, state):
        l = self.common_model(state)

        mean = self.mean_model(l)
        logstd = self.logstd_model(l)

        return self.tfpd([tf.tanh(mean), tf.clip_by_value(tf.exp(logstd), 0.1, 1.0)])