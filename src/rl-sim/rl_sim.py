import sys
import os
import inspect
from matplotlib import pyplot as plt
from tqdm import tqdm
import numpy as np

this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
root_folder = os.path.dirname(this_folder)
sys.path.append(root_folder + '\\otm')
sys.path.append(root_folder + '\\agents')
from otm_env import *

class rlGlue:

    def __init__(self, env_init_info, agent_init_info, algo, num_rewards = None):

        self.avg_reward_buffer = []
        self.reward_buffer = []
        self.num_rewards = num_rewards
        self.env = otmEnv(env_init_info)

        if algo == "linear_q_learning":
            import lin_q_learning as lql
            one_vec = np.ones(self.env.otm4rl.num_stages * self.env.otm4rl.num_intersections)
            agent_init_info["state_ranges"] = [one_vec*0, one_vec]
            agent_init_info["num_actions"] = self.env.otm4rl.num_stages ** self.env.otm4rl.num_intersections
            self.agent = lql.LinQLearningAgent(agent_init_info)
            self.env.state_division = self.agent.num_tiles * self.agent.num_tilings - self.agent.num_tilings + 1

        elif algo == "tabular_q_learning":
            import tab_q_learning as tql
            self.agent = tql.TabQLearningAgent(agent_init_info)
        else:
            raise("Algorithm " + str(algo) + " not found!")

    def start(self, initial_state):
        self.env.start()
        state = self.env.reset(initial_state)
        return self.agent.agent_start(state)

    def step(self, action):
        state, reward, _ = self.env.step(action)
        self.add_reward_buffer(reward)
        return self.agent.agent_step(reward, state)

    def run_steps(self, initial_action, num_steps):
        action = self.step(initial_action)
        for i in tqdm(range(num_steps-1)):
            action = self.step(action)
        return action

    def add_reward_buffer(self, reward):
        if self.num_rewards != None:
            self.reward_buffer.append(reward)
            if len(self.reward_buffer) % self.num_rewards == 0:
                self.avg_reward_buffer.append(np.mean(self.reward_buffer))
                self.reward_buffer = []

    def train_agent(self, initial_state, num_steps):
        initial_action = self.start(initial_state)
        self.run_steps(initial_action, num_steps)
        self.end()

    def test_rl_policy(self, initial_state, num_steps, buffer = True):
        performance = 0
        old_buffer = self.env.buffer
        self.env.buffer = buffer
        self.env.start()
        state = self.env.reset(initial_state)
        for i in tqdm(range(num_steps)):
            state, reward, avg_reward = self.env.step(self.agent.greedy_policy(state), compute_reward = True)
            performance += avg_reward
        self.env.buffer = old_buffer
        self.end()
        return performance/num_steps

    def end(self):
        self.env.close()

    def plot_avg_reward(self):
        if self.num_rewards != None:
            plt.plot(range(self.num_rewards, len(self.avg_reward_buffer)*self.num_rewards + 1, self.num_rewards), -np.array(self.avg_reward_buffer))
            plt.xlabel("Number of time steps")
            plt.title("Average negative reward over " + str(self.num_rewards) + " time steps")
            plt.show()
        else:
            print("Rewards were not saved during this experiment. Set num_rewards to a value greater than 0.")

class benchmarkTest:

    def __init__(self, env_init_info):
        self.env = otmEnv(env_init_info)
        self.env.close()

    def test_benchmark(self, initial_state, num_steps, buffer = True):
        performance = 0
        self.env.start()
        self.env.buffer = buffer
        state = self.env.reset(initial_state)

        for i in tqdm(range(num_steps*self.env.time_step)):
            self.env.add_signal_buffer()
            performance += self.env.advance(1, compute_reward = True)
            self.env.add_queue_buffer()

        self.env.close()

        return performance/(num_steps*self.env.time_step)

    def plot_agg_queue(self, c_id, stage_id, queue_type, plot_hlines = True, plot_signals = True, start = 0, end = None):

        link_ids = self.env.otm4rl.in_link_ids[c_id][stage_id]
        ymax = np.sum([self.env.otm4rl.max_queues[link_id] for link_id in link_ids])
        ylim = (0, ymax*1.05)
        if plot_hlines and self.env.state_division != None:
            if queue_type == "waiting":
                ybars = [ymax*i/self.env.state_division for i in range(1, self.env.state_division + 1)]
            else:
                ybars = [ymax]
        else:
            ybars = None
        title = "Agg. Queue Dynamics: Controller " + str(c_id) + ", Stage " + str(stage_id) + " - " + queue_type + " queue"
        green_stages = [stage_id]
        queue_vec = np.array([self.env.queue_buffer[link_id][queue_type][start:end] for link_id in link_ids]).sum(axis=0)
        queue_times = list(range(len(queue_vec)))
        if plot_signals:
            signal_vec = self.env.signal_buffer[c_id][start:end]
            signal_times = list(range(len(queue_vec)))
        else:
            signal_vec = None
            signal_times = None

        self.env.plot.plot_queue(ylim, title, green_stages, queue_vec, queue_times, signal_vec, signal_times, ybars)
