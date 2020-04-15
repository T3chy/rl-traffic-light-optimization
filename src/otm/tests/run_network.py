import os
import inspect
from OTMWrapper import OTMWrapper
from matplotlib import pyplot as plt

# define the input file
this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
root_folder = os.path.dirname(os.path.dirname(this_folder))
root_folder = os.path.dirname(os.path.dirname(root_folder))
print(root_folder)
configfile = os.path.join(root_folder,'capstone-project', 'cfg', 'network_tests.xml')

# open the api
otm = OTMWrapper(configfile)

# Plot the network
otm.show_network(4)

# # run a simulation
otm.run_simple(start_time=0,duration=600,output_dt=10)

# # extract the state trajectory
Y = otm.get_state_trajectory()

# # plot the state trajectory
fig = plt.figure()
plt.subplot(311)
plt.plot(Y['time'],Y['vehs'].T[:,1:4])
plt.ylabel("vehicles")
plt.title("OTM simulation result")
plt.subplot(312)
plt.plot(Y['time'],Y['flows_vph'].T[:,1:4])
plt.ylabel("flow [vph]")
plt.subplot(313)
plt.plot(Y['time'],Y['speed_kph'].T[:,1:4])
plt.ylabel("speed [kph]")
plt.legend(['link 1','link 2','link 3'])
plt.xlabel("time [sec]")
plt.draw()

plt.show()

# # always end by deleting the wrapper
del otm
