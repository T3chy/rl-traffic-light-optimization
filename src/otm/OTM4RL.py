from OTMWrapper import OTMWrapper
import os
import inspect

class OTM4RL:

    def __init__(self, configfile, jaxb_only=False):
        this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        root_folder = os.path.dirname(os.path.dirname(this_folder))
        cfg = os.path.join(root_folder,'cfg', configfile)
        self.otmwrapper = OTMWrapper(cfg)

    # GET STATIC -----------------------------------------

    def get_link_ids(self):
        return self.otmwrapper.otm.scenario().get_link_ids()

    def get_road_connection_info(self):

        road_connections = {1: {"in_link":1, "out_link":2},
                            2: {"in_link":2, "out_link":13},
                            3: {"in_link":2, "out_link":3},
                            4: {"in_link":3, "out_link":19},
                            5: {"in_link":3, "out_link":4},
                            6: {"in_link":4, "out_link":25},
                            7: {"in_link":4, "out_link":5},
                            8: {"in_link":6, "out_link":7},
                            9: {"in_link":7, "out_link":28},
                            10: {"in_link":7, "out_link":8},
                            11: {"in_link":8, "out_link":22},
                            12: {"in_link":8, "out_link":9},
                            13: {"in_link":9, "out_link":16},
                            14: {"in_link":9, "out_link":10},
                            15: {"in_link":11, "out_link":12},
                            16: {"in_link":12, "out_link":10},
                            17: {"in_link":12, "out_link":13},
                            18: {"in_link":14, "out_link":15},
                            19: {"in_link":15, "out_link":3},
                            20: {"in_link":15, "out_link":16},
                            21: {"in_link":17, "out_link":18},
                            22: {"in_link":18, "out_link":9},
                            23: {"in_link":18, "out_link":19},
                            24: {"in_link":20, "out_link":21},
                            25: {"in_link":21, "out_link":4},
                            26: {"in_link":21, "out_link":22},
                            27: {"in_link":23, "out_link":24},
                            28: {"in_link":24, "out_link":8},
                            29: {"in_link":24, "out_link":25},
                            30: {"in_link":26, "out_link":27},
                            31: {"in_link":27, "out_link":5},
                            32: {"in_link":27, "out_link":28}}
        return road_connections

    def get_max_queues(self):
        max_queues = {}
        for link_id in self.otmwrapper.otm.scenario().get_link_ids():
            link = self.otmwrapper.otm.scenario().get_link_with_id(link_id)
            max_queues[link_id] = link.get_jam_density_vpkpl() * link.getFull_length() * link.getFull_lanes() / 1000
        return max_queues

    # returns map from signal id to to a signal object (a dict)
    # psig['node_id']
    # psig['phases'] a map from p"phase_id" to phase object (a dict)
    #       x['rcs'] ... a set of road connection ids
    #       x['y'] ... yellow_time
    #       x['r'] ... red_clear_time
    #       x['ming'] ... min_green_time
    def get_signals(self):
        X = {}
        for oact in self.otmwrapper.otm.scenario().get_actuators():
            if str(oact.getType())=='signal':
                psig = {}
                psig['node_id'] = oact.getTarget_id()
                psig['phases'] = {}
                for phase in oact.get_phases():
                    x = {}
                    x['road_conns'] = phase.getRoad_connections()
                    x['yellow_time'] = phase.getYellow_time()
                    x['red_clear_time'] = phase.getRed_clear_time()
                    x['min_green_time'] = phase.getMin_green_time()
                    psig['phases'][phase.getId()] = x
                X[oact.getId()] = psig

        return X

    # returns map from controller id to a controller object (a dict)
    # X['cycle']
    # X['offset']
    # X['stages'] an ordered list of stage dicts:
    #   x['duration']
    #   x['phases']
    def get_controller_infos(self):
        X = {} # id to controller
        for ocntrl in self.otmwrapper.otm.scenario().get_controller_infos():
            if str(ocntrl.getType())=='sig_pretimed':

                cntrl = {}
                cntrl['cycle'] = ocntrl.getCycle()
                cntrl['offset'] = ocntrl.getOffset()

                stages = []
                for ostage in ocntrl.getStages():
                    stage = {}
                    stage['duration'] = ostage.getDuration()
                    stage['phases'] = ostage.getPhases()
                    stages.append(stage)

                cntrl['stages'] = stages
                X[ocntrl.getId()] = cntrl

        return X

    #     # list of dictionary
    #     # for controller in self.otmwrapper.otm.scenario().get_controllers():
    #     #     if str(controller.getType())::'sig_pretimed':
    #     #         print(controller)
    #     #         print(controller.getPretimed_signal_info())
    #     #         schedule : controller.getPretimed_signal_info().getSchedule()
    #     #         stagelist : schedule[0].getStages()
    #     #         # cntrl : {}
    #     #         # cntrl['id'] : int(controller.getId())
    #     #         # cntrl['stages'] : []

    #     return X

    # GET STATE AND ACTION -----------------------------------------

    def get_queues(self):
        otm = self.otmwrapper.otm
        queues = {}
        for link_id in self.get_link_ids():
            X = self.otmwrapper.otm.scenario().get_link_queues(link_id)
            queues[link_id] = {'waiting': round(X.waiting()),'transit': round(X.transit())}
        return queues

    # returns a dictionary from controller id to stage index
    def get_control(self):
        X = {}
        for ctrl_id in self.otmwrapper.otm.scenario().get_controller_ids():
            cntrl = self.otmwrapper.otm.scenario().get_actual_controller_with_id(ctrl_id)
            X[ctrl_id] = cntrl.get_stage_index()
        return X

    # SET STATE AND ACTION -----------------------------------------

    def set_queues(self,queue_dictionary):
        for link_id, q4link in queue_dictionary.items():
            self.otmwrapper.otm.scenario().set_link_vehicles(link_id, round(q4link['waiting']), round(q4link['transit']))

    # action is a dictionary from controller id to stage index
    def set_control(self,action):
        for ctrl_id, stage_index in action.items():
            cntrl = self.otmwrapper.otm.scenario().get_actual_controller_with_id(ctrl_id)
            cntrl.set_stage_index(int(stage_index))

    # RUN -----------------------------------------
    def initialize(self):
        self.otmwrapper.initialize(float(0))
        self.otmwrapper.otm.advance(float(1))

    def advance(self, duration):
        self.otmwrapper.otm.advance(float(duration))
