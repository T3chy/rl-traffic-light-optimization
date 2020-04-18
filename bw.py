import numpy as np
import math
import scipy.optimize as opt

def modhalf(a,cycle):
    return math.fmod(a+cycle/2,cycle)-cycle/2

class Intersection:

    def __init__(self, name, cycle, gi, go, delta):
        self.name = name

        # pretimed green window
        self.cycle = cycle
        self.gi = gi            # [sec] incoming green time
        self.go = go            # [sec] outgoing green time
        self.delta = modhalf(delta,cycle)  # [sec] internal offset
        self.absoffseto = np.nan
        self.absoffseti = np.nan
        self.reloffseto = np.nan
        self.reloffseti = np.nan
            

class Artery:

    def __init__(self, cycle):
        self.cycle = cycle          # [sec] cycle time for coordination
        self.intersection = []      # n intersections
        self.vi = []                # [mps] n-1 inbound speeds
        self.vo = []                # [mps] n-1 outbound speeds
        self.to = []                # [sec] n-1 inbound travel times
        self.ti = []                # [sec] n-1 outbound travel times
        self.optbandwidth = np.nan  # [sec] optimal total bandwidth
        self.optbo = np.nan         # [sec] optimal outbound bandwidth
        self.optbi = np.nan         # [sec] optimal inbound bandwidth

    def addIntersection(self, i):
        i.myArtery = self
        self.intersection.append(i)

    def addSegment(self, L_m, vi_kph, vo_kph):
        vi = vi_kph * 1000/3600
        vo = vo_kph * 1000/3600
        self.vi.append(vi)
        self.vo.append(vo)
        self.to.append(L_m/vo)
        self.ti.append(-L_m/vi)

    ###################
    # given Go, Gi, delta0, go, gi
    #       0     n-2  n-1  n
    # x = [o2 ... on   b    bbar]'
    # max ( b + bbar )
    # s.t. b \pm (oi - oj) < Go(i,j) for all pairs i,j in 2...n i~=j
    #      b \pm oi < Go(1,i)     i=2...n
    #      bbar \pm (oi - oj) < Gi(i,j) \mp delta0(i)-delta0(j) for all pairs i,j in 2...n i~=j
    #      bbar \pm wi < Gi(1,i) \mp (delta0(i)-delta0(1))   i=2...n
    #      b < min(go)
    #      bbar < min(gi)
    def optimize_pretimed_lp(self):
        
        n = len(self.intersection)

        # compute translated internal offsets .........
        delta0 = self.translated_internal_offsets()
        
        # green intervals ....................
        go = np.array([i.go for i in self.intersection])
        gi = np.array([i.gi for i in self.intersection])
        gstaro = min(go)
        gstari = min(gi)
        Go = ( np.tile(go,(n,1)) + np.transpose(np.tile(go,(n,1))) ) /2
        Gi = ( np.tile(gi,(n,1)) + np.transpose(np.tile(gi,(n,1))) ) /2

        # linear program ....................

        numvar = n+1
        A = []
        B = []
        b = n-1   # index to b in row
        bbar = n  # index to bbar in row

        d00 = delta0[0]

        for i in range(2,n+1):   # omega i with i=2...n
            
            oi = i-2    # index to omega i in row
            
            d0i = delta0[i-1]
            go1i = Go[0,i-1]
            gi1i = Gi[0,i-1]

            for j in range(2,n+1):   # omega j with j=2...n

                if i==j:
                    continue
                
                oj = j-2  # index to omega j in row

                Goij = Go[i-1,j-1]
                Giij = Gi[i-1,j-1]
                d0j = delta0[j-1]

                # b + wi - wj < Go(i,j) for all pairs i,j in 2...n i~=j
                row = np.zeros(numvar)
                row[b] = 1
                row[oi] = 1
                row[oj] = -1
                A.append(row)
                B.append(Goij)
                
                # bbar + oi - oj < Gi(i,j) - delta0(i) + delta0(j) for all pairs i,j in 2...n i~=j
                row = np.zeros(numvar)
                row[bbar] = 1
                row[oi] = 1
                row[oj] = -1
                A.append(row)
                B.append( Giij- d0i + d0j )
            
            # b + oi < Go(1,i)     i=2...n
            row = np.zeros(numvar)
            row[b] = 1
            row[oi] = 1
            A.append(row)
            B.append(go1i)
            
            # b - oi < Go(1,i)     i=2...n
            row = np.zeros(numvar)
            row[b] = 1
            row[oi] = -1
            A.append(row)
            B.append(go1i)
            
            # bbar + oi < Gi(1,i) - (delta0(i)-delta0(1))   i=2...n
            row = np.zeros(numvar)
            row[bbar] = 1
            row[oi] = 1
            A.append(row)
            B.append( gi1i - d0i + d00 )
            
            # bbar - oi < Gi(i) + (delta0(i)-delta0(1))   i=2...n
            row = np.zeros(numvar)
            row[bbar] = 1
            row[oi] = -1
            A.append(row)
            B.append( gi1i + d0i - d00 )
            
        # solve lp
        c = np.zeros(numvar)
        c[-2] = -1
        c[-1] = -1

        bounds = []
        for i in range(numvar-2):
            bounds.append( (None,None) )
        bounds.append( (0,gstaro) )
        bounds.append( (0,gstari) )

        sol = opt.linprog(c, A, B, bounds=bounds)
        fLstar = -sol.fun
        omegaL = sol.x[0:n]
        
        # apply the theorem ..............
        gstar = max(gstaro, gstari)

        if fLstar >= gstar:
            print('double band')
            omegaN = np.array(omegaL)
            bstar = sol.x[n-1]
            bbarstar = sol.x[n]
        else:
            print('single band')
            if gstaro >= gstari:   # outbound is dominant
                omegaN = np.zeros(n)
                bstar = gstar
                bbarstar = 0
            else:                  # inbound is dominant
                omegaN = [d00-d for d in delta0[1:]]
                omegaN.insert(0, 0.)     
                omegaN = np.array(omegaN)           
                bstar = 0
                bbarstar = gstar

        
        # set offsets on intersections ............
        self.set_outbound_relative_offsets(omegaN)
        
        return (bstar,bbarstar)
    
    def set_outbound_relative_offsets(self,omegaO):
        
        delta0 = self.translated_internal_offsets()
        omegaI = np.array( omegaO + delta0 - delta0[0] )
        omegaO = [modhalf(o,self.cycle) for o in omegaO]
        omegaI = [modhalf(o,self.cycle) for o in omegaI]
        
        # translate back into absolute offsets ...............
        thetaO, thetaI = self.relative2absolute(omegaO,omegaI)
        
        #  copy to intersections ................
        for i, intr in enumerate(self.intersection):
            intr.absoffseto = thetaO[i]
            intr.absoffseti = thetaI[i]
            intr.reloffseto = omegaO[i]
            intr.reloffseti = omegaI[i]

    def relative2absolute(self,omegaO,omegaI):   
        n = len(self.intersection)        
        thetaI = np.empty(n)
        thetaO = np.empty(n)
        thetaO[0] = 0.
        thetaI[0] = modhalf(self.intersection[0].delta,self.cycle)
        for i in range(1,n):
            thetaO[i] = omegaO[i] + thetaO[0] - omegaO[0] + sum(self.to[:i])
            thetaI[i] = omegaI[i] + thetaI[0] - omegaI[0] + sum(self.ti[:i])
        thetaO = [modhalf(t,self.cycle) for t in thetaO]
        thetaI = [modhalf(t,self.cycle) for t in thetaI]
        return (thetaO, thetaI)
    
    # compute delta0 from delta and travel times (equation 34)
    def translated_internal_offsets(self):

        n = len(self.intersection)

        # collect deltas
        delta = [i.delta for i in self.intersection]
        
        # Equation (34)
        delta0 = np.empty(n)  # [sec]
        sumtominusti = 0
        for i in range(n-1):
            delta0[i] = delta[i] + sumtominusti
            sumtominusti += self.to[i] - self.ti[i]
        delta0[-1] = delta[-1] + sumtominusti
    
        # correct wrt delta0
        # delta0 = [modhalf(d-delta0[0],self.cycle)+delta0[0] for d in delta0]
        delta0 = [modhalf(d,self.cycle) for d in delta0]
        
        return np.array(delta0)

    # def compute_band_pretimed(self,inorout)
        
    #     if strcmp(inorout,'in')
    #         absoffset = [self.intersection.absoffseti]
    #         reloffset = [self.intersection.reloffseti]
    #         green = [self.intersection.gi]
    #     else
    #         absoffset = [self.intersection.absoffseto]
    #         reloffset = [self.intersection.reloffseto]
    #         green = [self.intersection.go]
    #     end
        
    #     # bandoffset is the absolute offset of the center of the band
    #     interval = reloffset'*[1 1] + green'/2*[-1 1]
    #     a = max(interval(:,1))
    #     b = min(interval(:,2))
    #     if(b>a)
    #         band = b-a
    #         bandoffset = absoffset' - green'/2 + mean([a b]) - interval(:,1)
    #     else
    #         band = 0
    #         bandoffset = nan*absoffset
    #     end
        # retun (band, bandoffset)
    



    # def compute_total_bandwidth(self):
        
    #     reloffsetO = [self.intersection.reloffseto]
    #     reloffsetI = [self.intersection.reloffseti]
        
    #     #  compute band sizes
    #     band_o = compute_band_pretimed(obj,'out')
    #     band_i = compute_band_pretimed(obj,'in')
    #     total_band = band_o + band_i
                    
    #     return (total_band,band_o,band_i)

