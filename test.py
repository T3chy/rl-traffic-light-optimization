import bw
import datetime

cycle = 600.            # cycle in seconds

a = bw.Artery(cycle)
								# name         gi   go   delta
a.addIntersection(bw.Intersection('i2', cycle, 20., 30., 5.))
a.addSegment(200, 25, 35)
a.addIntersection(bw.Intersection('i3', cycle, 20., 50., 25.))
a.addSegment(200, 25, 35)
a.addIntersection(bw.Intersection('i4', cycle, 50., 10., 15.))

bstar, bbarstar = a.optimize_pretimed_lp()

for inter in a.intersection:
	print(f"{inter.name} : {inter.absoffseto}, {inter.absoffseti}")

print(bstar, bbarstar)
                                

