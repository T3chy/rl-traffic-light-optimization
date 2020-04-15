import numpy as np
import os
import inspect
import sys

otm_folder = os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
sys.path.append(otm_folder)

from otm_env import otmEnv
from env_plot import plotEnv

def get_env():
	this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	root_folder = os.path.dirname(os.path.dirname(os.path.dirname(this_folder)))
	configfile = os.path.join(root_folder,'cfg', 'network_1.xml')
	return otmEnv({"state_division": 2, "time_step": 60, "plot_precision": 4, "buffer": True}, configfile)

def test_plot_queue():
	plot = plotEnv()
	env = get_env()
	env.reset("random")

	for j in range(3):
		for i in range(2):
			env.otm4rl.set_control({1: i, 2: 0})
			env.add_signal_buffer()
			for j in range(env.plot_precision):
				env.otm4rl.otm.advance(float(env.time_step/env.plot_precision))
				env.add_queue_buffer()

	link_id = 2
	ymax = np.max(list(env.otm4rl.max_queues.values()))
	ylim = (0, ymax*1.1)
	ybars = [ymax/2,ymax]
	title = "Link 2 - Waiting queue"
	green_stages = env.otm4rl.in_link_info[link_id]["stages"]
	queue_vec = env.queue_buffer[link_id]["waiting"]
	signal_vec = env.signal_buffer[env.otm4rl.in_link_info[link_id]["controller"]]
	print(queue_vec)
	print(signal_vec)

	plot.plot_queue(env.time_step, env.plot_precision, ylim, title, green_stages, queue_vec, signal_vec, ybars)

	del env

# def test_get_signal_positions():
# 	env = get_env()
# 	env.reset()
# 	env.otm4rl.advance(100)
# 	control = env.otm4rl.get_control()
# 	state = env.otm4rl.get_queues()
# 	lines = env.build_network_lines(state)[0]
# 	print(env.get_signal_positions(lines, control))
#
# 	del env
#
# def test_plot_environment():
# 	env = get_env()
#
# 	env.reset()
# 	action = np.random.choice(env.action_space)
# 	state, reward = env.step(action)
# 	action = np.random.choice(env.action_space)
# 	state = env.otm4rl.get_queues()
# 	print(env.decode_action(action))
# 	env.plot_environment(state, env.decode_action(action))
# 	state, reward = env.step(action)
# 	action = np.random.choice(env.action_space)
# 	state = env.otm4rl.get_queues()
# 	print(env.decode_action(action))
# 	env.plot_environment(state, env.decode_action(action))
# 	state, reward = env.step(action)
# 	action = np.random.choice(env.action_space)
# 	state = env.otm4rl.get_queues()
# 	print(env.decode_action(action))
# 	env.plot_environment(state, env.decode_action(action))
#
# 	del env

if __name__ == '__main__':
	test_plot_queue()
