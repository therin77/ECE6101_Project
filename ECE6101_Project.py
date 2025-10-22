from numpy.random import default_rng
import numpy as np

#something wrong with times, too long??


def mm1(arrival_rate, service_rate, n, seed = 1234567):
    
    #constants
    rng = default_rng(seed)
    #arrive = depart = 0.0
    arrive = np.zeros((n,))
    depart = np.zeros((n,))
    delay = np.zeros((n,))
    num_pkt = np.zeros((n,))
    mean_interarrival_time = 1.0 / arrival_rate
    mean_service_time = 1.0 / service_rate
    
    print(mean_interarrival_time, mean_service_time)
    
    #loop through packets
    for i in range(0, n):
        arrive[i] = np.sum(arrive) + rng.exponential(mean_interarrival_time)
        if i == 1:
            start  = arrive[i]
            num_pkt[i] = 1
        if i != 1:
            start = max(arrive[i], depart[i-1])
            
            #num of pkts
            if arrive[i] >  depart[i-1]:
                num_pkt[i] =  1
            if  arrive[i] <  depart[i-1]:
                z = i-1
                c = 2
                while True:
                    if arrive[i] <  depart[z]:
                        z = z-1
                        c = c + 1
                    else:
                        num_pkt[i]  = c
                        break
            
        #start = max(arrive, depart)
        depart[i] = start + rng.exponential(mean_service_time)
        delay[i] = rng.exponential(mean_service_time)
        print(arrive[i], depart[i], delay[i])
        #print("%d,%f" % (i, start - arrive))
        
    avg_delay = 1/n*np.sum(delay)
    avg_pkt = 1/n*np.sum(num_pkt)
    #print(avg_delay, avg_pkt)


#############
#MAIN PROGRAM
#############

#initialize variables

arrival_rate = 50 #add ince 50-1200pkt/s 50 incr
C = 10e6  #link capacity/mu in bits/s
pkt_length = 1000*8 #bits per packet from bytes
n = 10 #50000 #number of packets

#convert C to pkts/s
C_conv = C*1/pkt_length

#first layer
mm1(arrival_rate, C_conv, n, seed=1234567)