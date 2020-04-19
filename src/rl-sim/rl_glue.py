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
        try:
            self.env.otm4rl
        except:
            self.env.start()

        state = self.env.reset(initial_state)
        return self.agent.agent_start(state)

    def step(self, action):
        state, reward = self.env.step(action)
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

    def test_policy(self, initial_state, num_steps, policy = None, buffer = True):
        performance = 0
        old_buffer = self.env.buffer
        self.env.buffer = buffer
        state = self.env.reset(initial_state)
        if policy == None:
            for i in range(num_steps):
                state, reward = self.env.step(self.agent.greedy_policy(state))
                performance += reward
        else:
            for i in range(num_steps):
                state, reward = self.env.step(policy[i])
                performance += reward
        self.env.buffer = old_buffer
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
