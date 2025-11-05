from numpy.random import default_rng
import numpy as np
import matplotlib.pyplot as plt


def mm1(arrival_rate, service_rate, n, seed = 1234567, a = 1, input = []):

    
    
    #initialize RNG
    rng = default_rng(seed)
   
    #initialize arrays
    arrive = np.zeros((n,))
    depart = np.zeros((n,))
    delay = np.zeros((n,))
    num_pkt = np.zeros((n,))
    
    #constants
    mean_interarrival_time = 1.0 / arrival_rate
    mean_service_time = 1.0 / service_rate
    
    
    #loop through packets
    for i in range(0, n):
        if a == 1:
            #generate inter-arrival
            int_arr = rng.exponential(mean_interarrival_time)
            #determine arrival in time and start of service
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
            
        if a == 2:
            
            #use arrival from past queue
            arrive[i] = input[i]
        
            #determine arrival in time and start of service
            if i == 0:
                start  = arrive[i]
                num_pkt[i] = 1
                
            if i != 0:
                
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
    
    return depart, avg_delay, avg_pkt

def rand_queue(N, n):
    
    num_queues = np.arange(N)
    prob = np.ones((len(num_queues), ))/N
    random_numbers = np.random.choice(num_queues, size=n, p=prob)
    
    return random_numbers
    
    
####################################################
#MAIN PROGRAM
####################################################

#initialize variables

arrival_rate_it = np.arange(50, 1200, 50) #add ince 50-1200pkt/s 50 incr
C = 10e6  #link capacity/mu in bits/s
pkt_length = 1000*8 #bits per packet from bytes
n = 100 #50000 #number of packets
N = 4 #simulation number

#list of arrival times for layer 2 queues
q1 = np.zeros((n,))
q2 = np.zeros((n,))
q3 = np.zeros((n,))
q4 = np.zeros((n,))

#list of average delay for each interarrival
de1_1 = np.zeros((len(arrival_rate_it),))
de2_1 = np.zeros((len(arrival_rate_it),))
de2_2 = np.zeros((len(arrival_rate_it),))
de2_3 = np.zeros((len(arrival_rate_it),))
de2_4 = np.zeros((len(arrival_rate_it),))
de3_1 = np.zeros((len(arrival_rate_it),))

#list of average num of pkts per system
pk1_1 = np.zeros((len(arrival_rate_it),))
pk2_1 = np.zeros((len(arrival_rate_it),))
pk2_2 = np.zeros((len(arrival_rate_it),))
pk2_3 = np.zeros((len(arrival_rate_it),))
pk2_4 = np.zeros((len(arrival_rate_it),))
pk3_1 = np.zeros((len(arrival_rate_it),))


#convert C to pkts/s
C_conv = C*1/pkt_length

for i in range(len(arrival_rate_it)):

    #set arrival rate for iteration
    arrival_rate = arrival_rate_it[i] 
    
    print(arrival_rate)
    
    #############
    #FIRST LAYER
    #############
    
    #sim through queue
    depart_lay1, de, s = mm1(arrival_rate, C_conv, n, seed=1234567, a =1)
    
    #set delay and packet for queues and arrival rate
    de1_1[i] = de
    pk1_1[i] = s
    
    
    #############
    #SECOND LAYER
    #############
    
    #determine prob of each queue and determine which queue used
    random_numbers = rand_queue(N, n)
    random_numbers_str = np.array([str(x) for x in random_numbers])
    
    if N == 4:
    
        #seperate into imput for queue
        q1 = depart_lay1[random_numbers_str == '0']
        q2 = depart_lay1[random_numbers_str == '1']
        q3 = depart_lay1[random_numbers_str == '2']
        q4 = depart_lay1[random_numbers_str == '3']
        
        #sim through queues
        depart_lay2_1, de1, s1 = mm1(arrival_rate, C_conv, len(q1), seed=1234567, a=2, input = q1)
        depart_lay2_2, de2, s2 = mm1(arrival_rate, C_conv, len(q2), seed=1234567, a=2, input = q2)
        depart_lay2_3, de3, s3 = mm1(arrival_rate, C_conv, len(q3), seed=1234567, a=2, input = q3)
        depart_lay2_4, de4, s4 = mm1(arrival_rate, C_conv, len(q4), seed=1234567, a=2, input = q4)
        
        #set delay and packet for queues and arrival rate
        de2_1[i] = de1
        de2_2[i] = de2
        de2_3[i] = de3
        de2_4[i] = de4
        
        pk2_1[i] = s1
        pk2_2[i] = s2
        pk2_3[i] = s3
        pk2_4[i] = s4
        
        q5 = np.concatenate((depart_lay2_1, depart_lay2_2, depart_lay2_3, depart_lay2_4), axis=0)
        q5 = np.sort(q5)
        
    if N == 3:
    
        #seperate into imput for queue
        q1 = depart_lay1[random_numbers_str == '0']
        q2 = depart_lay1[random_numbers_str == '1']
        q3 = depart_lay1[random_numbers_str == '2']
        
        #sim through queues
        depart_lay2_1, de1, s1 = mm1(arrival_rate, C_conv, len(q1), seed=1234567, a=2, input = q1)
        depart_lay2_2, de2, s2 = mm1(arrival_rate, C_conv, len(q2), seed=1234567, a=2, input = q2)
        depart_lay2_3, de3, s3 = mm1(arrival_rate, C_conv, len(q3), seed=1234567, a=2, input = q3)
        
        #set delay and packet for queues and arrival rate
        de2_1[i] = de1
        de2_2[i] = de2
        de2_3[i] = de3
        
        pk2_1[i] = s1
        pk2_2[i] = s2
        pk2_3[i] = s3
        
        q5 = np.concatenate((depart_lay2_1, depart_lay2_2, depart_lay2_3), axis=0)
        q5 = np.sort(q5)
        
    if N == 2:
        
        #seperate into imput for queue
        q1 = depart_lay1[random_numbers_str == '0']
        q2 = depart_lay1[random_numbers_str == '1']
    
        
        #sim through queues
        depart_lay2_1, de1, s1 = mm1(arrival_rate, C_conv, len(q1), seed=1234567, a=2, input = q1)
        depart_lay2_2, de2, s2 = mm1(arrival_rate, C_conv, len(q2), seed=1234567, a=2, input = q2)
        
        #set delay and packet for queues and arrival rate
        de2_1[i] = de1
        de2_2[i] = de2
        
        pk2_1[i] = s1
        pk2_2[i] = s2
    
        q5 = np.concatenate((depart_lay2_1, depart_lay2_2), axis=0)
        q5 = np.sort(q5)
        
    if N == 1:
        
        #seperate into imput for queue
        q1 = depart_lay1[random_numbers_str == '0']
    
        
        #sim through queues
        depart_lay2_1, de1, s1 = mm1(arrival_rate, C_conv, len(q1), seed=1234567, a=2, input = q1)
        
        #set delay and packet for queues and arrival rate
        de2_1[i] = de1
        pk2_1[i] = s1
    
        q5 = depart_lay2_1
    
    
    #############
    #THIRD LAYER
    #############
    
    #sim through queue
    depart_lay3_1, de, s = mm1(arrival_rate, C_conv, len(q5), seed=1234567, a=2, input = q5)

    #set delay and packet for queues and arrival rate
    de3_1[i] = de
    pk3_1[i] = s


#############
#PLOTTING
#############

#avg pkt delay

fig, axs = plt.subplots(3, 2, figsize=(10, 8), sharex=True, sharey=True)

axs[0, 0].plot(arrival_rate_it, de1_1, color='blue')
axs[0, 0].set_title('Queue 1-1')
axs[0, 0].set_xlabel("Arrival Rate")
axs[0, 0].set_ylabel("Average Packet Delay")

axs[0, 1].plot(arrival_rate_it, de2_1, color='green')
axs[0, 1].set_title('Queue 2-1')
axs[0, 1].set_xlabel("Arrival Rate")
axs[0, 1].set_ylabel("Average Packet Delay")

axs[1, 0].plot(arrival_rate_it, de2_2, color='red')
axs[1, 0].set_title('Queue 2-2')
axs[1, 0].set_xlabel("Arrival Rate")
axs[1, 0].set_ylabel("Average Packet Delay")

axs[1, 1].plot(arrival_rate_it, de2_3, color='purple')
axs[1, 1].set_title('Queue 2-3')
axs[1, 1].set_xlabel("Arrival Rate")
axs[1, 1].set_ylabel("Average Packet Delay")

axs[2, 0].plot(arrival_rate_it, de2_4, color='orange')
axs[2, 0].set_title('Queue 2-4')
axs[2, 0].set_xlabel("Arrival Rate")
axs[2, 0].set_ylabel("Average Packet Delay")

axs[2, 1].plot(arrival_rate_it, de3_1, color='black')
axs[2, 1].set_title('Queue 3-1')
axs[2, 1].set_xlabel("Arrival Rate")
axs[2, 1].set_ylabel("Average Packet Delay")

# Adjust layout to prevent titles and labels from overlapping
plt.tight_layout(rect=[0, 0.03, 1, 0.95])

plt.suptitle('Queue Avg Pkt Delay N = 1', fontsize=16)

# Display the plot
plt.show()

#avg num of pkts
fig, axs = plt.subplots(3, 2, figsize=(10, 8), sharex=True, sharey=True)

axs[0, 0].plot(arrival_rate_it, pk1_1, color='blue')
axs[0, 0].set_title('Queue 1-1')
axs[0, 0].set_xlabel("Arrival Rate")
axs[0, 0].set_ylabel("Average Number of Pkts")

axs[0, 1].plot(arrival_rate_it, pk2_1, color='green')
axs[0, 1].set_title('Queue 2-1')
axs[0, 1].set_xlabel("Arrival Rate")
axs[0, 1].set_ylabel("Average Number of Pkts")

axs[1, 0].plot(arrival_rate_it, pk2_2, color='red')
axs[1, 0].set_title('Queue 2-2')
axs[1, 0].set_xlabel("Arrival Rate")
axs[1, 0].set_ylabel("Average Number of Pkts")

axs[1, 1].plot(arrival_rate_it, pk2_3, color='purple')
axs[1, 1].set_title('Queue 2-3')
axs[1, 1].set_xlabel("Arrival Rate")
axs[1, 1].set_ylabel("Average Number of Pkts")

axs[2, 0].plot(arrival_rate_it, pk2_4, color='orange')
axs[2, 0].set_title('Queue 2-4')
axs[2, 0].set_xlabel("Arrival Rate")
axs[2, 0].set_ylabel("Average Number of Pkts")

axs[2, 1].plot(arrival_rate_it, pk3_1, color='black')
axs[2, 1].set_title('Queue 3-1')
axs[2, 1].set_xlabel("Arrival Rate")
axs[2, 1].set_ylabel("Average Number of Pkts")

# Adjust layout to prevent titles and labels from overlapping
plt.tight_layout(rect=[0, 0.03, 1, 0.95])

plt.suptitle('Queue Avg Num of Pkts N = 1', fontsize=16)

# Display the plot
plt.show()




