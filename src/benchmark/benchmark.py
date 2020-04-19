import bandwidth as bw

params = {
    "cycle": 240,
    "demand_arterial": {"outbond": 1500, "inbound": 1500},
    "capacity_arterial": [2000, 2000],
    "demand_cross": [750, 750],
    "capacity_cross":[1000, 1000]
}

class offsetOptimizer:

    def __init__(self, params):
        self.cycle = params["cycle"]
        self.demand_arterial = params["demand_arterial"]
        self.demand_cross = params["demand_cross"]
        self.capacity_arterial = params["capacity_arterial"]
        self.capacity_cross = params["capacity_cross"]
        self.num_intersections = len(self.demand_cross.keys())
        self.delta = params.get("delta", np.zeros(self.num_intersections))

    def setup_network(self, green_times):
        gi = green_times["inbound"]
        go = green_times["outbound"]
        network = bw.Artery(self.cycle)
        for i in range(self.num_intersections):
            network.addIntersection(bw.Intersection('i' + str(i+1), self.cycle, gi[i], go[i], self.delta[i]))
            if i != self.num_intersections - 1:
                network.addSegment(1000, 100, 100)
        return network

    def compute_green_times(self):
        green_times = dict()

        for stream in ["outbound", "inbound"]:
            fraction_gtime =  self.demand_arterial[stream]*np.array(self.capacity_cross)/(np.array(self.demand_cross)*np.array(capacity_arterial))
            green_times[stream] = self.cycle * fraction_gtime

        return green_times

cost_list = []


    fraction_cycle = cycle*0.67
    gi0 = fraction_cycle
    go0 = fraction_cycle
    gi1 = fraction_cycle
    go1 = fraction_cycle



    bstar, bbarstar = a.optimize_pretimed_lp()
    cost = bstar + bbarstar
    cost_list.append(cost)


    for inter in a.intersection:
        print(f"{inter.name} : {inter.absoffseto}, {inter.absoffseti}")

    print("cost list = ", cost_list)
