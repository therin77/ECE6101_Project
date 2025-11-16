from numpy.random import default_rng
import numpy as np
import matplotlib.pyplot as plt


def mm1(arrival_rate, service_rate, n, seed = 1234567, a = 1, input = []):

    
    #initialize RNG
    #rng = default_rng(seed)
    rng = np.random.default_rng()
   
    #initialize arrays
    arrive = np.zeros((n,))
    depart = np.zeros((n,))
    delay = np.zeros((n,))
    serv_time = np.zeros((n,))
    
    #constants
    mean_interarrival_time = 1.0 / arrival_rate
    mean_service_time = 1.0 / service_rate
    
    
    #loop through packets
    for i in range(0, n):
        
        #genrate interarrival times
        if a == 1:
            #generate inter-arrival
            int_arr = rng.exponential(mean_interarrival_time)
            
            #determine arrival in time and start of service
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
        
            #determine arrival in time and start of service
            if i == 0:
                start  = arrive[i]
                
            if i != 0:
                start = max(arrive[i], depart[i-1])
                
        serv_time[i] = rng.exponential(mean_service_time)
        depart[i] = start + serv_time[i]
        delay[i] = start - arrive[i] + serv_time[i]
        
    avg_delay = 1/n*np.sum(delay)
    avg_pkt = arrival_rate*avg_delay
    #avg_pkt = 1/n*np.sum(num_pkt)
    #avg_delay = avg_pkt/arrival_rate
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
n = 50000 #number of packets
N_int = [1, 2, 3, 4] #simulation number

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

for k in range(len(N_int)):
    
    N = N_int[k]

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
    #THEORETICAL VALUES
    #############
    
    theo_delay_1_1 = 1/(C_conv*np.ones((len(arrival_rate_it),)) - arrival_rate_it)
    theo_delay_2_1 = 1/(C_conv*np.ones((len(arrival_rate_it),)) - arrival_rate_it/N)
    theo_delay_3_1 = 1/(C_conv*np.ones((len(arrival_rate_it),)) - arrival_rate_it)
    
    theo_num_1_1 = arrival_rate_it*theo_delay_1_1
    theo_num_2_1 = arrival_rate_it/N*theo_delay_2_1
    theo_num_3_1 = arrival_rate_it*theo_delay_3_1
    
    #############
    #DIFFERENCE SIM/THEO
    #############
    
    dif_del_1_1 = np.absolute(theo_delay_1_1 - de1_1)
    dif_del_2_1 = np.absolute(theo_delay_2_1 - de2_1)
    dif_del_3_1 = np.absolute(theo_delay_3_1 - de3_1)
    
    dif_pkt_1_1 = np.absolute(theo_num_1_1 - pk1_1)
    dif_pkt_2_1 = np.absolute(theo_num_2_1 - pk2_1)
    dif_pkt_3_1 = np.absolute(theo_num_3_1 - pk3_1)
    
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
    
    #avg pkt delay
    
    fig, axs = plt.subplots(3, 2, figsize=(10, 8), sharex=False, sharey=False)
    
    axs[0, 0].plot(arrival_rate_it, de1_1, color='blue')
    axs[0, 0].plot(arrival_rate_it, theo_delay_1_1, color='green')
    axs[0, 0].set_title('Queue 1-1')
    axs[0, 0].set_xlabel("Arrival Rate")
    axs[0, 0].set_ylabel("Average Packet Delay")
    
    axs[1, 0].plot(arrival_rate_it, de2_1, color='blue')
    axs[1, 0].plot(arrival_rate_it, theo_delay_2_1, color='green')
    axs[1, 0].set_title('Queue 2-1')
    axs[1, 0].set_xlabel("Arrival Rate")
    axs[1, 0].set_ylabel("Average Packet Delay")
    
    axs[2, 0].plot(arrival_rate_it, de3_1, color='blue')
    axs[2, 0].plot(arrival_rate_it, theo_delay_3_1, color='green')
    axs[2, 0].set_title('Queue 3-1')
    axs[2, 0].set_xlabel("Arrival Rate")
    axs[2, 0].set_ylabel("Average Packet Delay")
    
    axs[0, 1].plot(arrival_rate_it, pk1_1, color='blue')
    axs[0, 1].plot(arrival_rate_it, theo_num_1_1, color='green')
    axs[0, 1].set_title('Queue 1-1')
    axs[0, 1].set_xlabel("Arrival Rate")
    axs[0, 1].set_ylabel("Average Number of Pkts")
    
    axs[1, 1].plot(arrival_rate_it, pk2_1, color='blue')
    axs[1, 1].plot(arrival_rate_it, theo_num_2_1, color='green')
    axs[1, 1].set_title('Queue 2-1')
    axs[1, 1].set_xlabel("Arrival Rate")
    axs[1, 1].set_ylabel("Average Number of Pkts")
    
    axs[2, 1].plot(arrival_rate_it, pk3_1, color='blue')
    axs[2, 1].plot(arrival_rate_it, theo_num_3_1, color='green')
    axs[2, 1].set_title('Queue 3-1')
    axs[2, 1].set_xlabel("Arrival Rate")
    axs[2, 1].set_ylabel("Average Number of Pkts")
    
    
    # Adjust layout to prevent titles and labels from overlapping
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    plt.suptitle('Queue Avg Values N = ' + str(N), fontsize=16)
    
    labels = ['Sim.', 'Theor.']
    
    fig.legend(labels, loc='lower right', bbox_to_anchor=(1,-0.1), ncol=len(labels), bbox_transform=fig.transFigure)
    
    # Display the plot
    plt.show()

#############
#PLOT DIFF SIM VS THEO
#############

#1-1

fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=False, sharey=False)

for i, row in enumerate(del_1_1):
    axs[0].plot(arrival_rate_it, row)
axs[0].plot(arrival_rate_it, dif_del_1_1, color='green')
axs[0].set_title('Queue 1-1 Delay')
axs[0].set_xlabel("Arrival Rate")
axs[0].set_ylabel("Difference")

for i, row in enumerate(pkt_1_1):
    axs[1].plot(arrival_rate_it, row)
axs[1].plot(arrival_rate_it, dif_pkt_1_1, color='green')
axs[1].set_title('Queue 1-1 Packet')
axs[1].set_xlabel("Arrival Rate")
axs[1].set_ylabel("Difference")


# Adjust layout to prevent titles and labels from overlapping
plt.tight_layout(rect=[0, 0.03, 1, 0.95])

plt.suptitle('Difference Theo VS Sim 1-1', fontsize=16)

labels = ['N=1', 'N=2', 'N=3', 'N=4']

fig.legend(labels, loc='lower right', bbox_to_anchor=(1,-0.1), ncol=len(labels), bbox_transform=fig.transFigure)

# Display the plot
plt.show()

#2-1

fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=False, sharey=False)

for i, row in enumerate(del_2_1):
    axs[0].plot(arrival_rate_it, row)
axs[0].set_title('Queue 2-1 Delay')
axs[0].set_xlabel("Arrival Rate")
axs[0].set_ylabel("Difference")

for i, row in enumerate(pkt_2_1):
    axs[1].plot(arrival_rate_it, row)
axs[1].set_title('Queue 2-1 Packet')
axs[1].set_xlabel("Arrival Rate")
axs[1].set_ylabel("Difference")


# Adjust layout to prevent titles and labels from overlapping
plt.tight_layout(rect=[0, 0.03, 1, 0.95])

plt.suptitle('Difference Theo VS Sim 2-1', fontsize=16)

labels = ['N=1', 'N=2', 'N=3', 'N=4']

fig.legend(labels, loc='lower right', bbox_to_anchor=(1,-0.1), ncol=len(labels), bbox_transform=fig.transFigure)

# Display the plot
plt.show()

#3-1

fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=False, sharey=False)

for i, row in enumerate(del_3_1):
    axs[0].plot(arrival_rate_it, row)
axs[0].set_title('Queue 3-1 Delay')
axs[0].set_xlabel("Arrival Rate")
axs[0].set_ylabel("Difference")

for i, row in enumerate(pkt_3_1):
    axs[1].plot(arrival_rate_it, row)
axs[1].set_title('Queue 3-1 Packet')
axs[1].set_xlabel("Arrival Rate")
axs[1].set_ylabel("Difference")


# Adjust layout to prevent titles and labels from overlapping
plt.tight_layout(rect=[0, 0.03, 1, 0.95])

plt.suptitle('Difference Theo VS Sim 3-1', fontsize=16)

labels = ['N=1', 'N=2', 'N=3', 'N=4']

fig.legend(labels, loc='lower right', bbox_to_anchor=(1,-0.1), ncol=len(labels), bbox_transform=fig.transFigure)

# Display the plot
plt.show()

