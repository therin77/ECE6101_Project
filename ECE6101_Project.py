from numpy.random import default_rng
import numpy as np


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
    
    
    #loop through packets
    for i in range(0, n):
        
        #generate inter-arrival
        int_arr = rng.exponential(mean_interarrival_time)
        
        #determine arrival  in time and start of service
        if i == 0:
            arrive[i] = int_arr
            start  = arrive[i]
            num_pkt[i] = 1
            
        if i != 0:
            arrive[i] = arrive[i-1] + int_arr
            start = max(arrive[i], depart[i-1])
            
            #num of pkts in system
            if arrive[i] >  depart[i-1]:
                num_pkt[i] =  1
            if  arrive[i] <  depart[i-1]:
                z = i-1
                c = 1
                while True:
                    if arrive[i] <  depart[z]:
                        z = z-1
                        c = c + 1
                    else:
                        num_pkt[i]  = c
                        break
       
        delay[i] = rng.exponential(mean_service_time)
        depart[i] = start + delay[i]
        
    avg_delay = 1/n*np.sum(delay)
    avg_pkt = 1/n*np.sum(num_pkt)
    print(avg_delay, avg_pkt)
    
    return depart

def rand_queue(N, n):
    
    num_queues = np.arange(N)
    prob = np.ones((len(num_queues), ))/N
    random_numbers = np.random.choice(num_queues, size=n, p=prob)
    
    return random_numbers
    
    
    
####################################################
#MAIN PROGRAM
####################################################

#initialize variables

arrival_rate = 50 #add ince 50-1200pkt/s 50 incr
C = 10e6  #link capacity/mu in bits/s
pkt_length = 1000*8 #bits per packet from bytes
n = 10 #50000 #number of packets
N = 4 #simulation number

q1 = np.zeros((n,))
q2 = np.zeros((n,))
q3 = np.zeros((n,))
q4 = np.zeros((n,))

#convert C to pkts/s
C_conv = C*1/pkt_length

#############
#FIRST LAYER
#############

depart_lay1 = mm1(arrival_rate, C_conv, n, seed=1234567)


#############
#SECOND LAYER
#############

#determine prob of each queue and determine which queue used
random_numbers = rand_queue(N, n)
random_numbers_str = [str(x) for x in random_numbers]
print(random_numbers_str)

#run each queue

q1 = depart_lay1[random_numbers_str == '0']
#q2 = depart_lay1[random_numbers == 1]
#q3 = depart_lay1[random_numbers == 2]
#q4 = depart_lay1[random_numbers == 3]
print(q1)

"""
combined_and_sorted = sorted(zip(random_numbers, depart_lay1))

queue_num, times= zip(*combined_and_sorted)

for i in range(combined_and_sorted):
    
    if queue_num()
    

print(combined_and_sorted[1])
"""

"""
arr1 = np.array([10, 20, 30, 40, 50, 60, 70])
arr2 = np.array(['A', 'B', 'A', 'C', 'B', 'A', 'C'])

# Split based on 'A' in arr2
split_A = arr1[arr2 == 'A']
print(f"Elements corresponding to 'A': {split_A}")

# Split based on 'B' in arr2
split_B = arr1[arr2 == 'B']
print(f"Elements corresponding to 'B': {split_B}")
"""




