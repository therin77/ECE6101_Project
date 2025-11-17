##################################
#ECE6101 Project: Simulate system of queues for study of Kleinrock’s Independence Approximation
#Developed by: Kate Gothberg
#Last Edited: 11/17/2025
##################################

#modules used
import numpy as np
import matplotlib.pyplot as plt

debug = 0

#queue : simulates queues of system
#loosely based of this guy's code: https://stackoverflow.com/questions/73384766/simple-m-m-1-queuing-simulation-with-simpy-departure-placement-issue
#inputs:
#   -arrival rate: if a = 1, use to sim arrival times, else unused
#   -service rate: rate of service of server
#   -n: number of packets to be served
#   -a: if a = 1: generate interarrival times,  a = 2: interarrival based on inpout array
#   -input: if a = 2, input array of interarrival times
#outputs:
#   -depart: departure times of each packet served
#   -avg_delay: average time in subsystem for each packet
#   -avg_pkt: average number of packets in subsystem (via Little's Law)
def queue(arrival_rate, service_rate, n, a = 1, input = []):
 
    #initialize RNG
    rng = np.random.default_rng()
   
    #initialize arrays
    arrive = np.zeros((n,))
    depart = np.zeros((n,))
    delay = np.zeros((n,))
    serv_time = np.zeros((n,))
    
    #constants
    mean_interarrival_time = 1.0 / arrival_rate
    mean_service_time = 1.0 / service_rate
    
    #loop through simulation for each packet
    for i in range(0, n):
        
        #if no input array, generate interarrival times and time packet in system
        if a == 1:
            
            #generate inter-arrival
            int_arr = rng.exponential(mean_interarrival_time)
            
            #determine arrival and start time of service
            if i == 0:
                arrive[i] = int_arr
                start  = arrive[i]
                
            if i != 0:
                arrive[i] = arrive[i-1] + int_arr
                start = max(arrive[i], depart[i-1])
               
        #interarrival from outputs of previous queue
        if a == 2:
            
            #use arrival from past queue
            arrive[i] = input[i]
        
            #determine arrival and start time of service
            if i == 0:
                start  = arrive[i]
                
            if i != 0:
                start = max(arrive[i], depart[i-1])
                
        #calculate service time, departure time, and time in system
        serv_time[i] = rng.exponential(mean_service_time)
        depart[i] = start + serv_time[i]
        delay[i] = start - arrive[i] + serv_time[i]
        
    #calculate average delay via average and avg num of packets via Little's Law
    avg_delay = 1/n*np.sum(delay)
    avg_pkt = arrival_rate*avg_delay
    
    if debug == 1:
        print(avg_delay, avg_pkt)
    
    return depart, avg_delay, avg_pkt

#rand_queue : random routing, aka which queue is chosen per packet
#inputs:
#   -N: number of queues
#   -n: number of packets
#outputs:
#   -random_numbers: vector of which queue for each packet
def rand_queue(N, n):
    
    #create range of N queues, find prob for each if equi-probable, then assign queue/packet
    num_queues = np.arange(N)
    prob = np.ones((len(num_queues), ))/N
    random_numbers = np.random.choice(num_queues, size=n, p=prob)
    
    return random_numbers
    
    
####################################################
#MAIN PROGRAM
####################################################

#############
#INITIALIZE VARIABLES
#############

#given in project description
arrival_rate_it = np.arange(50, 1200, 50) #add ince 50-1200pkt/s 50 incr
C = 10e6                                  #link capacity/mu in bits/s
pkt_length = 1000*8                       #bits per packet from bytes
n = 50000                                 #number of packets
N_int = [1, 2, 3, 4]                      #simulation number

#############
#INITIALIZE VECTORS
#############

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


#convert C to pkts/s so same units
C_conv = C*1/pkt_length

#############
#ITERATE # OF QUEUES
#############
for k in range(len(N_int)):
    
    #set number of queues for iteration
    N = N_int[k]
    
    #############
    #ITERATE ARRIVAL TIMES
    #############
    for i in range(len(arrival_rate_it)):
    
        #set arrival rate for iteration
        arrival_rate = arrival_rate_it[i] 
        
        if debug == 1:
            print(arrival_rate)
            print("Delay :     # pkt:")
        
        #############
        #FIRST LAYER
        #############
        
        #sim through queue
        depart_lay1, de, s = queue(arrival_rate, C_conv, n, a =1)
        
        #set delay and packet for arrival rate
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
            depart_lay2_1, de1, s1 = queue(arrival_rate, C_conv, len(q1), a=2, input = q1)
            depart_lay2_2, de2, s2 = queue(arrival_rate, C_conv, len(q2), a=2, input = q2)
            depart_lay2_3, de3, s3 = queue(arrival_rate, C_conv, len(q3), a=2, input = q3)
            depart_lay2_4, de4, s4 = queue(arrival_rate, C_conv, len(q4), a=2, input = q4)
            
            #set delay and packet for specific queue and arrival rate
            de2_1[i] = de1
            de2_2[i] = de2
            de2_3[i] = de3
            de2_4[i] = de4
            
            pk2_1[i] = s1
            pk2_2[i] = s2
            pk2_3[i] = s3
            pk2_4[i] = s4
            
            #combine all depart times to 1 stream for 3rd layer
            q5 = np.concatenate((depart_lay2_1, depart_lay2_2, depart_lay2_3, depart_lay2_4), axis=0)
            q5 = np.sort(q5)
            
        if N == 3:
        
            #seperate into imput for queue
            q1 = depart_lay1[random_numbers_str == '0']
            q2 = depart_lay1[random_numbers_str == '1']
            q3 = depart_lay1[random_numbers_str == '2']
            
            #sim through queues
            depart_lay2_1, de1, s1 = queue(arrival_rate, C_conv, len(q1), a=2, input = q1)
            depart_lay2_2, de2, s2 = queue(arrival_rate, C_conv, len(q2), a=2, input = q2)
            depart_lay2_3, de3, s3 = queue(arrival_rate, C_conv, len(q3), a=2, input = q3)
            
            #set delay and packet for specific queue and arrival rate
            de2_1[i] = de1
            de2_2[i] = de2
            de2_3[i] = de3
            
            pk2_1[i] = s1
            pk2_2[i] = s2
            pk2_3[i] = s3
            
            #combine all depart times to 1 stream for 3rd layer
            q5 = np.concatenate((depart_lay2_1, depart_lay2_2, depart_lay2_3), axis=0)
            q5 = np.sort(q5)
            
        if N == 2:
            
            #seperate into imput for queue
            q1 = depart_lay1[random_numbers_str == '0']
            q2 = depart_lay1[random_numbers_str == '1']
        
            
            #sim through queues
            depart_lay2_1, de1, s1 = queue(arrival_rate, C_conv, len(q1), a=2, input = q1)
            depart_lay2_2, de2, s2 = queue(arrival_rate, C_conv, len(q2), a=2, input = q2)
            
            #set delay and packet for specific queue and arrival rate
            de2_1[i] = de1
            de2_2[i] = de2
            
            pk2_1[i] = s1
            pk2_2[i] = s2
            
            #combine all depart times to 1 stream for 3rd layer
            q5 = np.concatenate((depart_lay2_1, depart_lay2_2), axis=0)
            q5 = np.sort(q5)
            
        if N == 1:
            
            #seperate into imput for queue
            q1 = depart_lay1[random_numbers_str == '0']
        
            
            #sim through queues
            depart_lay2_1, de1, s1 = queue(arrival_rate, C_conv, len(q1), a=2, input = q1)
            
            #set delay and packet for specific queue and arrival rate
            de2_1[i] = de1
            pk2_1[i] = s1
        
            #combine all depart times to 1 stream for 3rd layer
            q5 = depart_lay2_1
        
        #############
        #THIRD LAYER
        #############
        
        #sim through queue
        depart_lay3_1, de, s = queue(arrival_rate, C_conv, len(q5), a=2, input = q5)
    
        #set delay and packet for queue and arrival rate
        de3_1[i] = de
        pk3_1[i] = s
    
    
    #############
    #CALC THEORETICAL VALUES
    #############
    
    #theoretical delay M/M/1 queue
    theo_delay_1_1 = 1/(C_conv*np.ones((len(arrival_rate_it),)) - arrival_rate_it)
    theo_delay_2_1 = 1/(C_conv*np.ones((len(arrival_rate_it),)) - arrival_rate_it/N)
    theo_delay_3_1 = 1/(C_conv*np.ones((len(arrival_rate_it),)) - arrival_rate_it)
    
    #theoretical # of packets M/M/1 queue
    theo_num_1_1 = arrival_rate_it*theo_delay_1_1
    theo_num_2_1 = arrival_rate_it/N*theo_delay_2_1
    theo_num_3_1 = arrival_rate_it*theo_delay_3_1
    
    #############
    #CALC DIFFERENCE SIM/THEO
    #############
    
    #difference delay theo vs sim
    dif_del_1_1 = np.absolute(theo_delay_1_1 - de1_1)
    dif_del_2_1 = np.absolute(theo_delay_2_1 - de2_1)
    dif_del_3_1 = np.absolute(theo_delay_3_1 - de3_1)
    
    #difference delay theo vs sim
    dif_pkt_1_1 = np.absolute(theo_num_1_1 - pk1_1)
    dif_pkt_2_1 = np.absolute(theo_num_2_1 - pk2_1)
    dif_pkt_3_1 = np.absolute(theo_num_3_1 - pk3_1)
    
    #turn differences into matrix so can plot all 4 N options
    if N == 1:
        del_1_1 = dif_del_1_1
        del_2_1 = dif_del_2_1
        del_3_1 = dif_del_3_1
        
        pkt_1_1 = dif_del_1_1
        pkt_2_1 = dif_pkt_2_1
        pkt_3_1 = dif_pkt_3_1
        
    if N != 1:
    
        del_1_1 = np.vstack([del_1_1, dif_del_1_1])
        del_2_1 = np.vstack([del_2_1, dif_del_2_1])
        del_3_1 = np.vstack([del_3_1, dif_del_3_1])
        
        pkt_1_1 = np.vstack([pkt_1_1, dif_pkt_1_1])
        pkt_2_1 = np.vstack([pkt_2_1, dif_pkt_2_1])
        pkt_3_1 = np.vstack([pkt_3_1, dif_pkt_3_1])
    
    
    #############
    #PLOT SIM VS THEO
    #############
    
    #plot for each N
    
    fig, axs = plt.subplots(3, 2, figsize=(10, 8), sharex=False, sharey=False)
    
    axs[0, 0].plot(arrival_rate_it, de1_1, color='blue')
    axs[0, 0].plot(arrival_rate_it, theo_delay_1_1, color='green')
    axs[0, 0].set_title('Queue 1-1 Delay')
    axs[0, 0].set_xlabel("Arrival Rate (pkt/s)")
    axs[0, 0].set_ylabel("Average Packet Delay (s)")
    
    axs[1, 0].plot(arrival_rate_it, de2_1, color='blue')
    axs[1, 0].plot(arrival_rate_it, theo_delay_2_1, color='green')
    axs[1, 0].set_title('Queue 2-1 Delay')
    axs[1, 0].set_xlabel("Arrival Rate (pkt/s)")
    axs[1, 0].set_ylabel("Average Packet Delay (s)")
    
    axs[2, 0].plot(arrival_rate_it, de3_1, color='blue')
    axs[2, 0].plot(arrival_rate_it, theo_delay_3_1, color='green')
    axs[2, 0].set_title('Queue 3-1 Delay')
    axs[2, 0].set_xlabel("Arrival Rate (pkt/s)")
    axs[2, 0].set_ylabel("Average Packet Delay (s)")
    
    axs[0, 1].plot(arrival_rate_it, pk1_1, color='blue')
    axs[0, 1].plot(arrival_rate_it, theo_num_1_1, color='green')
    axs[0, 1].set_title('Queue 1-1 Num. of Packets')
    axs[0, 1].set_xlabel("Arrival Rate (pkt/s)")
    axs[0, 1].set_ylabel("Average Number of Pkts")
    
    axs[1, 1].plot(arrival_rate_it, pk2_1, color='blue')
    axs[1, 1].plot(arrival_rate_it, theo_num_2_1, color='green')
    axs[1, 1].set_title('Queue 2-1 Num. of Packets')
    axs[1, 1].set_xlabel("Arrival Rate (pkt/s)")
    axs[1, 1].set_ylabel("Average Number of Pkts")
    
    axs[2, 1].plot(arrival_rate_it, pk3_1, color='blue')
    axs[2, 1].plot(arrival_rate_it, theo_num_3_1, color='green')
    axs[2, 1].set_title('Queue 3-1 Num. of Packets')
    axs[2, 1].set_xlabel("Arrival Rate (pkt/s)")
    axs[2, 1].set_ylabel("Average Number of Pkts")
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.suptitle('Queue Avg Values N = ' + str(N), fontsize=16)
    labels = ['Sim.', 'Theor.']
    fig.legend(labels, loc='lower right', bbox_to_anchor=(1,-0.1), ncol=len(labels), bbox_transform=fig.transFigure)
    plt.show()

#############
#PLOT DIFF SIM VS THEO
#############

#Queue 1-1

fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=False, sharey=False)

#iterate over each N
for i, row in enumerate(del_1_1):
    axs[0].plot(arrival_rate_it, row, label='N = ' + str(i+1))
axs[0].set_title('Queue 1-1 Delay')
axs[0].set_xlabel("Arrival Rate (pkt/s)")
axs[0].set_ylabel("Difference (s)")
axs[0].legend(loc='upper left')

#iterate over each N
for i, row in enumerate(pkt_1_1):
    axs[1].plot(arrival_rate_it, row, label='N = ' + str(i+1))
axs[1].set_title('Queue 1-1 Num. of Packets')
axs[1].set_xlabel("Arrival Rate (pkt/s)")
axs[1].set_ylabel("Difference")
axs[1].legend(loc='upper left')

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.suptitle('Difference Theo VS Sim 1-1', fontsize=16)
plt.show()

#Queue 2-1

fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=False, sharey=False)

#iterate over each N
for i, row in enumerate(del_2_1):
    axs[0].plot(arrival_rate_it, row, label='N = ' + str(i+1))
axs[0].set_title('Queue 2-1 Delay')
axs[0].set_xlabel("Arrival Rate (pkt/s)")
axs[0].set_ylabel("Difference (s)")
axs[0].legend(loc='upper left')

#iterate over each N
for i, row in enumerate(pkt_2_1):
    axs[1].plot(arrival_rate_it, row, label='N = ' + str(i+1))
axs[1].set_title('Queue 2-1 Num. of Packets')
axs[1].set_xlabel("Arrival Rate (pkt/s)")
axs[1].set_ylabel("Difference")
axs[1].legend(loc='upper left')

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.suptitle('Difference Theo VS Sim 2-1', fontsize=16)
plt.show()

#Queue 3-1

fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=False, sharey=False)

#iterate over each N
for i, row in enumerate(del_3_1):
    axs[0].plot(arrival_rate_it, row, label='N = ' + str(i+1))
axs[0].set_title('Queue 3-1 Delay')
axs[0].set_xlabel("Arrival Rate (pkt/s)")
axs[0].set_ylabel("Difference")
axs[0].legend(loc='upper left')

#iterate over each N
for i, row in enumerate(pkt_3_1):
    axs[1].plot(arrival_rate_it, row, label='N = ' + str(i+1))
axs[1].set_title('Queue 3-1 Num. of Packets')
axs[1].set_xlabel("Arrival Rate (pkt/s)")
axs[1].set_ylabel("Difference")
axs[1].legend(loc='upper left')

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.suptitle('Difference Theo VS Sim 3-1', fontsize=16)
plt.show()

