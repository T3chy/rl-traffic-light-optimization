import numpy as np
from OTM4RL import OTM4RL
from env_plot import plotEnv
from random import sample

class otmEnv:

    def __init__(self, env_init_info, configfile):

        self.configfile = configfile
        self.state_division = env_init_info.get("state_division", None)
        self.time_step = env_init_info["time_step"]
        self.plot_precision = env_init_info["plot_precision"]
        assert (type(self.plot_precision) == int and self.plot_precision >= 1), "plot_precision must be an integer greater than or equal to 1"
        self.buffer = env_init_info["buffer"]
        self.start()
        self.action_space = range(self.otm4rl.num_stages ** self.otm4rl.num_intersections)
        if self.buffer:
            self.network_lines = self.otm4rl.get_network_lines()
        self.plot = plotEnv()
        # self.seed()

    # def seed(self, seed=None):
    #     self.np_random, seed = seeding.np_random(seed)
    #     return [seed]

    def start(self):
        try:
            self.close()
        except:
            pass
        self.otm4rl = OTM4RL(self.configfile)
        self.otm4rl.initialize(float(0))
        self.otm4rl.otm.advance(float(1))

    def reset(self, set_queues = "random"):
         if self.buffer:
             self.queue_buffer = dict(list(zip(self.otm4rl.link_ids, [{"waiting": [], "transit": []} for i in self.otm4rl.link_ids])))
             self.signal_buffer = dict(list(zip(self.otm4rl.controllers.keys(), [[] for i in self.otm4rl.controllers.keys()])))
         if set_queues == "random":
             self.set_state(self.random_queues())
         elif set_queues == "current":
             self.state = self.q2state(self.otm4rl.get_queues())
             self.add_queue_buffer()
         else:
             self.set_state(set_queues)

         return self.state

    def step(self, action):
        assert action in self.action_space, "%r (%s) invalid" % (action, type(action))

        self.otm4rl.set_control(self.decode_action(action))
        self.add_signal_buffer()

        for i in range(self.plot_precision):
            self.otm4rl.otm.advance(self.time_step/self.plot_precision)
            self.add_queue_buffer()

        queues = self.otm4rl.get_queues()

        self.state = self.q2state(queues)

        try:
            reward = -np.sum(np.where(self.state >= 1, self.state_division - 1, (self.state * self.state_division).astype(int)))
        except:
            reward = -np.sum(self.state)

        return self.state, reward

    def set_state(self, queues):
        self.otm4rl.set_queues(queues)
        self.state = self.q2state(self.otm4rl.get_queues())
        self.add_queue_buffer()

    def q2state(self, queues):
        state_vec = []
        i = 0
        for c_id, controller in self.otm4rl.controllers.items():
            stages = controller["stages"]
            for i, stage in enumerate(stages):
                agg_queue = 0
                max_queue = 0
                for link_id in self.otm4rl.in_link_ids[c_id][i]:
                    agg_queue += queues[link_id]["waiting"]
                    max_queue += self.otm4rl.max_queues[link_id]
                state_vec.append(agg_queue/max_queue)
        return np.array(state_vec)

    def decode_action(self, action):
        a = action
        controller_ids = list(self.otm4rl.controllers.keys())
        signal_command = dict(list(zip(controller_ids, np.zeros(self.otm4rl.num_stages).astype(int))))
        i = - 1
        while a != 0:
            controller_id = controller_ids[i]
            signal_command[controller_id] = a % self.otm4rl.num_stages
            a = a // self.otm4rl.num_stages
            i -= 1

        return signal_command

    def random_queues(self):
        rand_q = dict()
        for link_id in self.otm4rl.max_queues.keys():
           if link_id in self.otm4rl.out_links:
               rand_q[link_id] = {"waiting": int(0), "transit": int(0)}
           else:
               p = np.random.random()
               transit_queue = p*self.otm4rl.max_queues[link_id]
               q = np.random.random()
               waiting_queue = q*(self.otm4rl.max_queues[link_id] - transit_queue)
               rand_q[link_id] = {"waiting": round(waiting_queue), "transit": round(transit_queue)}
        return rand_q

    def add_queue_buffer(self):

        if self.buffer == True:
            queues = self.otm4rl.get_queues()
            for link_id in queues.keys():
                self.queue_buffer[link_id]["waiting"].append(queues[link_id]["waiting"])
                self.queue_buffer[link_id]["transit"].append(queues[link_id]["transit"])
        else:
            pass

    def add_signal_buffer(self):

        if self.buffer == True:
            signals = self.otm4rl.get_control()
            for c_id in signals:
                self.signal_buffer[c_id].append(signals[c_id])
        else:
            pass

    def plot_agg_queue(self, c_id, stage_id, queue_type, plot_hlines = True, plot_signals = True, start = 0, end = None):

        link_ids = self.otm4rl.in_link_ids[c_id][stage_id]
        ymax = np.sum([self.otm4rl.max_queues[link_id] for link_id in link_ids])
        ylim = (0, ymax*1.05)
        if plot_hlines:
            if queue_type == "waiting":
                ybars = [ymax*i/self.state_division for i in range(1, self.state_division + 1)]
            else:
                ybars = [ymax]
        else:
            ybars = None
        title = "Agg. Queue Dynamics: Controller " + str(c_id) + ", Stage " + str(stage_id) + " - " + queue_type + " queue"
        green_stages = [stage_id]
        queue_vec = np.array([self.queue_buffer[link_id][queue_type][start:end] for link_id in link_ids]).sum(axis=0)
        if plot_signals:
            signal_vec = self.signal_buffer[c_id]
        else:
            signal_vec = None

        self.plot.plot_queue(self.time_step, self.plot_precision, ylim, title, green_stages, queue_vec, signal_vec, ybars)

    def plot_link_queue(self, link_id, queue_type, plot_hlines = True, plot_signals = True, start = 0, end = None):

        try:
            link_controller = self.otm4rl.in_link_info[link_id]["controller"]
            green_stages = self.otm4rl.in_link_info[link_id]["stages"]
        except:
            print("This link is leaving the network or it is a demand link, so it is not impacted by traffic lights")
            return

        ymax = self.otm4rl.max_queues[link_id]
        ylim = (0, ymax*1.05)
        if plot_hlines:
            ybars = [ymax]
        else:
            ybars = None
        title = "Queue Dynamics: Link " + str(link_id) + " - " + queue_type + " queue"
        queue_vec = self.queue_buffer[link_id][queue_type][start:end]
        if plot_signals:
            signal_vec = self.signal_buffer[link_controller]
        else:
            signal_vec = None

        self.plot.plot_queue(self.time_step, self.plot_precision, ylim, title, green_stages, queue_vec, signal_vec, ybars)

    # def plot_network_gradient(self):
    #     self.plot.network_gradient(self.otm4rl.get_queues(), self.otm4rl.get_control())

    def close(self):
        del self.otm4rl

    # def render(self, mode='human'):
    #     #plot the queue profile over time
    #     #render the network
    #     pass
    #
    # def close(self):
    #     #stop rendering
    #     pass
