# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 00:55:22 2020

@author: laeti
"""
from itertools import combinations
from itertools import product
import bw
import datetime
import matplotlib.pyplot as plt

def optimization():
    
    max_cost = 0
    for cycle in range(60,121,30):
        print("\n")
        print("cycle=", cycle)
        print("\n")
        
        for gi0 in range(0,cycle, int(cycle/3)):
            for go0 in range(0,cycle, int(cycle/3)):
                for gi1 in range(0,cycle, int(cycle/3)):
                    for go1 in range(0,cycle, int(cycle/3)):
                        for gi2 in range(0,cycle, int(cycle/3)):
                            for go2 in range(0,cycle, int(cycle/3)):
                                
                                
                                a = bw.Artery(cycle)
                                a.addIntersection(bw.Intersection('i2', cycle, gi0, go0, 0))
                                a.addSegment(200, 25, 35)
                                a.addIntersection(bw.Intersection('i3', cycle, gi1, go1, 0))
                                a.addSegment(200, 25, 35)
                                a.addIntersection(bw.Intersection('i4', cycle, gi2, go2, 0))

                                bstar, bbarstar = a.optimize_pretimed_lp()
                                cost = bstar + bbarstar
                                if cost >= max_cost:
                                    max_cost = cost                                    
                                    optimized_parameters = [cycle, gi0, go0, gi1, go1, gi2, go2]
                                    

    print("\n")
    print("max_cost =", max_cost)
    print("\n")
    print (optimized_parameters)
    return max_cost


def optimization_2intersection_fixedcyle():
    
    
    cost_list = []
    

    cycle = 240
    fraction_cycle = cycle*0.67
    gi0 = fraction_cycle
    go0 = fraction_cycle
    gi1 = fraction_cycle
    go1 = fraction_cycle                              
                                
    a = bw.Artery(cycle)
    a.addIntersection(bw.Intersection('i2', cycle, gi0, go0, 0))
    a.addSegment(200, 25, 35)
    a.addIntersection(bw.Intersection('i3', cycle, gi1, go1, 0))
        
    bstar, bbarstar = a.optimize_pretimed_lp()
    cost = bstar + bbarstar
    cost_list.append(cost)
    
        
    for inter in a.intersection:
        print(f"{inter.name} : {inter.absoffseto}, {inter.absoffseti}")                      

    print("cost list = ", cost_list)

def optimization_2intersection_cycle():
    
    
    cost_list = []
    

    for cycle in range(1,601):
        fraction_cycle = cycle*0.67
        gi0 = fraction_cycle
        go0 = fraction_cycle
        gi1 = fraction_cycle
        go1 = fraction_cycle                              
                                
        a = bw.Artery(cycle)
        a.addIntersection(bw.Intersection('i2', cycle, gi0, go0, 0))
        a.addSegment(200, 25, 35)
        a.addIntersection(bw.Intersection('i3', cycle, gi1, go1, 0))
        
        bstar, bbarstar = a.optimize_pretimed_lp()
        cost = bstar + bbarstar
        cost_list.append(cost)
        
    return cost_list


cost_list = optimization_2intersection_cycle()

plt.plot([i for i in range(1,601)], cost_list)
plt.xlabel('Cycle')
plt.ylabel('Bandwidth')
plt.show
    
    
    
    
def optimization2():
    
    cost_list = []
    for cycle in range(0,120):
        print("\n")
        print("cycle=", cycle)
        print("\n")
        P = list(product(range(cycle), repeat=6))
        
        for k in range(0,len(P)):                       
            a = bw.Artery(cycle)
            a.addIntersection(bw.Intersection('i2', cycle, float(P[k][0]), float(P[k][1]), 0))
            a.addSegment(200, 25, 35)
            a.addIntersection(bw.Intersection('i3', cycle, float(P[k][2]), float(P[k][3]), 0))
            a.addSegment(200, 25, 35)
            a.addIntersection(bw.Intersection('i4', cycle,float(P[k][4]), float(P[k][5]), 0))
        
            bstar, bbarstar = a.optimize_pretimed_lp()
            cost = bstar + bbarstar
            cost_list.append(cost)
            
    max_value = max(cost_list)
    print("The maximum value is equal to:", max_value)




def test():
    initial_time = datetime.datetime.now()
    cycle = 20
    a = bw.Artery(cycle)
    a.addIntersection(bw.Intersection('i2', cycle, 6, 10, 0))
    a.addSegment(200, 25, 35)
    a.addIntersection(bw.Intersection('i3', cycle, 5, 10, 0))
    a.addSegment(200, 25, 35)
    a.addIntersection(bw.Intersection('i4', cycle, 5, 15, 0))

    bstar, bbarstar = a.optimize_pretimed_lp()
    cost = bstar + bbarstar
    final_time = datetime.datetime.now()
    time = final_time -  initial_time
    print (time*1000)
    
    

if __name__ == '__main__':
    #optimization()
    #optimization2()
    #optimization_2intersection_fixedcyle()
    optimization_2intersection_cycle()
    #test()
