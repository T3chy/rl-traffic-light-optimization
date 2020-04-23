import bandwidth as bw
import numpy as np
from tqdm import tqdm

class offsetOptimizer:

    def __init__(self, params):
        self.cycle = params["cycle"]
        self.demand_arterial = params["demand_arterial"]
        self.demand_cross = params["demand_cross"]
        self.capacity_arterial = params["capacity_arterial"]
        self.capacity_cross = params["capacity_cross"]
        # self.grid_delta = params["grid_delta"]
        # self.grid_size = params["grid_size"]
        # self.cost_threshold = params["cost_threshold"]
        self.num_intersections = len(self.capacity_arterial)
        self.delta = params.get("delta", np.zeros(self.num_intersections))
        self.fraction_gtime = self.get_fraction_gtime()

    def setup_network(self, green_times):
        network = bw.Artery(self.cycle)
        for i in range(self.num_intersections):
            network.addIntersection(bw.Intersection('i' + str(i+1), self.cycle, green_times[i], green_times[i], self.delta[i]))
            if i != self.num_intersections - 1:
                network.addSegment(1000, 100, 100)
        return network

    def get_fraction_gtime(self):
        ratio =  self.demand_arterial*np.array(self.capacity_cross)/(np.array(self.demand_cross)*np.array(self.capacity_arterial))
        fraction_gtime = ratio/(ratio + 1)
        return fraction_gtime

    def optimize(self):
        green_times = self.fraction_gtime * self.cycle
        network = self.setup_network(green_times)
        bstar, bbarstar, _ = network.optimize_pretimed_lp()
        cost = bstar + bbarstar
        offsets = []

        for inter in network.intersection:
            absoffseto = inter.absoffseto if inter.absoffseto >=0 else self.cycle + inter.absoffseto
            absoffseti = inter.absoffseti if inter.absoffseti >=0 else self.cycle + inter.absoffseti
            assert round(absoffseto, 2) == round(absoffseti, 2), "Inbound and outbund offsets for intersection " + inter.name + " not matching!"
            offsets.append(inter.absoffseto)

        return offsets, green_times, cost


    # def optimize_offset_grid(self, fraction_gtime, grid_delta):
    #     num_choices = self.grid_size * 2 + 1
    #     num_params = self.num_intersections * 2
    #     max_cost = 0
    #     for i in tqdm(range(num_choices ** num_params)):
    #         p = - self.grid_size*self.grid_delta + 1
    #         f_gtime = {"outbound": p * fraction_gtime["outbound"], "inbound": p * fraction_gtime["inbound"]}
    #         a = i
    #         j = - 1
    #         while a != 0:
    #             p = (((a % num_choices) - self.grid_size)*self.grid_delta + 1)
    #             if (-j-1) // self.num_intersections == 0:
    #                 f_gtime["outbound"][(-j-1) % self.num_intersections] = p * fraction_gtime["outbound"][(-j-1) % self.num_intersections]
    #             if (-j-1) // self.num_intersections == 1:
    #                 f_gtime["inbound"][(-j-1) % self.num_intersections] = p * fraction_gtime["inbound"][(-j-1) % self.num_intersections]
    #             a = a // num_choices
    #             j -= 1
    #         green_times = self.compute_green_times(f_gtime)
    #         network = self.setup_network(green_times)
    #         offsets, cost = self.optimize_offset_network(network)
    #         if cost > max_cost:
    #             max_cost = cost
    #             max_offsets = offsets.copy()
    #             max_fgtime = f_gtime.copy()
    #
    #     return max_offsets, max_cost, max_fgtime
    #
    # def optimize_offset(self):
    #     old_cost = 0
    #     grid_delta = self.grid_delta
    #     offsets, cost, fraction_gtime = self.optimize_offset_grid(self.fraction_gtime, grid_delta)
    #     print(cost, self.fraction_gtime)
    #     while (cost - old_cost)/old_cost > self.cost_threshold:
    #         old_cost = cost
    #         grid_delta /= self.grid_size
    #         offsets, cost, fraction_gtime = self.optimize_offset_grid(fraction_gtime, grid_delta)
    #         print(cost, fraction_gtime)
    #
    #     return offsets
