import os
import inspect
import numpy as np
from OTM4RL import OTM4RL

# GET STATIC -----------------------------------------

def test_get_link_ids(configfile):
	otm4rl = OTM4RL(configfile)
	print(otm4rl.link_ids)

	del otm4rl

def test_get_node_ids(configfile):
	otm4rl = OTM4RL(configfile)
	print(otm4rl.node_ids)

	del otm4rl

def test_get_controller_infos(configfile):
	otm4rl = OTM4RL(configfile)
	X = otm4rl.controllers

	print('cycle',X[2]['cycle'])
	print('offset',X[2]['offset'])
	for i,stage in enumerate(X[2]['stages']):
		print(i,'duration',stage['duration'])
		print(i,'phases',stage['phases'])
	del otm4rl

def test_get_signals(configfile):
	otm4rl = OTM4RL(configfile)
	X = otm4rl.signals

	print('node_id',X[2]['node_id'])
	for phaseid,phase in X[2]['phases'].items():
		print(phaseid,'road_conns',phase['road_conns'])
		print(phaseid,'yellow_time',phase['yellow_time'])
		print(phaseid,'red_clear_time',phase['red_clear_time'])
		print(phaseid,'min_green_time',phase['min_green_time'])

	del otm4rl

def test_get_road_connection_info(configfile):
	otm4rl = OTM4RL(configfile)
	print(otm4rl.road_connection_info)

	del otm4rl

def test_get_max_queues(configfile):
	otm4rl = OTM4RL(configfile)
	print(otm4rl.max_queues)

	del otm4rl

def test_get_in_link_ids(configfile):
	otm4rl = OTM4RL(configfile)
	print(otm4rl.in_link_ids)

	del otm4rl

def test_get_in_link_info(configfile):
	otm4rl = OTM4RL(configfile)
	print(otm4rl.in_link_info)

	del otm4rl

def test_get_out_links(configfile):
	otm4rl = OTM4RL(configfile)
	print(otm4rl.out_links)

	del otm4rl

def test_get_network_lines(configfile):
	otm4rl = OTM4RL(configfile)
	print(otm4rl.get_network_lines())

	del otm4rl

def test_get_num_stages(configfile):
	otm4rl = OTM4RL(configfile)
	print(otm4rl.num_stages)

	del otm4rl

def test_get_num_intersections(configfile):
	otm4rl = OTM4RL(configfile)
	print(otm4rl.num_intersections)

	del otm4rl

# GET STATE AND ACTION -----------------------------------------

def test_get_queues(configfile):
	otm4rl = OTM4RL(configfile)
	otm4rl.initialize(float(0))

	otm4rl.otm.advance(float(500))
	queues = otm4rl.get_queues()
	print(queues)
	otm4rl.otm.advance(float(700))
	queues = otm4rl.get_queues()
	print(queues)
	otm4rl.otm.advance(float(250))
	queues = otm4rl.get_queues()
	print(queues)

	del otm4rl

def test_get_control(configfile):
	otm4rl = OTM4RL(configfile)
	otm4rl.initialize(float(0))
	print(otm4rl.get_control())
	otm4rl.otm.advance(float(650))
	print(otm4rl.get_control())

	del otm4rl

# SET STATE AND ACTION -----------------------------------------

def test_set_queues(configfile):
	otm4rl = OTM4RL(configfile)
	myqueues = {
	1: {"waiting": 3, "transit": 5},
	2: {"waiting": 5, "transit": 3}
	}

	otm4rl.initialize(float(0))
	otm4rl.otm.advance(float(3000))

	print( otm4rl.get_queues() )

	otm4rl.set_queues(myqueues)

	print( otm4rl.get_queues() )

	otm4rl.otm.advance(float(2300))

	print( otm4rl.get_queues() )

	del otm4rl

def test_set_control(configfile):
	otm4rl = OTM4RL(configfile)
	otm4rl.initialize(float(0))
	otm4rl.otm.advance(float(70))

	# action[controller_id] = active stage id

	print(otm4rl.get_control())
	print(otm4rl.get_queues())

	otm4rl.set_control({1:1,2:0})
	print(otm4rl.get_queues())
	otm4rl.otm.advance(float(30))

	print(otm4rl.get_control())
	print(otm4rl.get_queues())

	del otm4rl


if __name__ == '__main__':
	this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	root_folder = os.path.dirname(os.path.dirname(this_folder))
	configfile = os.path.join(root_folder,'cfg', 'network_tests.xml')

	# test_get_link_ids(configfile)
	# test_get_node_ids(configfile)
	# test_get_controller_infos(configfile)
	# test_get_signals(configfile)
	# test_get_road_connection_info(configfile)
	# test_get_max_queues(configfile)
	# test_get_in_link_ids(configfile)
	# test_get_in_link_info(configfile)
	test_get_out_links(configfile)
	# test_get_num_stages(configfile)
	# test_get_num_intersections(configfile)
	# test_get_network_lines(configfile)
	# test_get_queues(configfile)
	# test_get_control(configfile)
	# test_set_queues(configfile)
	# test_set_control(configfile)
