#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys
import os
import inspect
from matplotlib import pyplot as plt
from tqdm import tqdm


# In[2]:


this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
root_folder = os.path.dirname(this_folder)


# In[3]:


sys.path.append(this_folder + '/../otm')
from otm_env import *
sys.path.append(this_folder+ '/../agents')


# In[4]:

configfile = 'network_1.xml'

env_init_info = {
    "time_step": 30,
    "plot_precision": 2,
    "buffer": False,
    "state_division": 7,
    "configfile": configfile
}


env = otmEnv(env_init_info)

agent_init_info = {
            "num_states": env_init_info["state_division"]**(env.otm4rl.num_intersections * env.otm4rl.num_stages),
            "num_actions": env.otm4rl.num_stages**env.otm4rl.num_intersections,
            "state_division": env.state_division,
            "epsilon": 1,
            "step_size": 0.1,
            "discount": 0.95,
            "seed": 0
            }

agent = ddpg_torch.Agent(agent_init_info)


# In[5]:


acc_neg_reward = [] # Contains negative sum of rewards during episode
num_steps = 20000   # The number of steps to run the simulation
reward_sum = 0

obs = env.reset("current")
action = agent.choose_action(obs)

for i in tqdm(range(num_steps)):

    action = agent.choose_action(obs)
    state, reward = env.step(action)
    agent.remember(obs,action,reward,state,0)
    agent.learn()
    obs = state
    reward_sum += reward

    if (i+1) % 200 == 0:
        acc_neg_reward.append(-reward_sum/200)
        reward_sum = 0

    if (i+1) % (num_steps/5) == 0:
        agent.epsilon -= 0.2
        print("Time-step: " + str(i+1) + "/" + str(num_steps))
        plt.plot(range(len(acc_neg_reward)), acc_neg_reward)
        plt.xlabel("Number of time steps")
        plt.title("Average negative reward over 50 time steps")
        plt.show()

env.close()


# In[6]:


plt.plot(range(len(acc_neg_reward)), acc_neg_reward)
plt.xlabel("Number of time steps")
plt.title("Average negative reward over 50 time steps")


# In[7]:


agent.q


# In[8]:


env.start()
env.buffer = True
state = env.reset("current")
rewards = []
for i in range(300):
    state = agent.encode_state(state)
    action = agent.argmax(agent.q[state])
    state, reward = env.step(action)
    rewards.append(reward)

print(np.mean(rewards[-10:]))


# In[9]:


env.plot_agg_queue(1, 0, "waiting", plot_signals = False)
env.plot_agg_queue(1, 0, "waiting", start = 8000)


# In[10]:


env.plot_agg_queue(1, 1, "waiting", plot_signals = False)
env.plot_agg_queue(1, 1, "waiting", start = 8000)


# In[11]:


env.plot_agg_queue(2, 0, "waiting", plot_signals = False)
env.plot_agg_queue(2, 0, "waiting", start = 8000)


# In[12]:


env.plot_agg_queue(2, 1, "waiting", plot_signals = False)
env.plot_agg_queue(2, 1, "waiting", start = 8000)


# In[13]:


env.close()


# In[ ]:
