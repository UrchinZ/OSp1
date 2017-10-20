#!/usr/bin/env python
#Xinyue Yan (yanx3)
#Judy Zhang (zhangz17)

import sys
import numpy
import string
import os
import copy

def parse_file(filename):
	f = open(filename)
	task = []
	row  = numpy.empty(4)
	sim = numpy.empty(4)
	for line in f:
		if line[0] == '#' or line[0] == '\n':
			continue
		n = 0
		for v in line.split('|'):
			if n == 0:
				task.append(v)
			else:
				row[n-1] = int(v)
			n=n+1
		sim = numpy.vstack([sim, row])
	f.close()
	sim = numpy.delete(sim, (0), axis=0)
	sim = sim.astype('int')
	"""
	print("<proc-id>|<initial-arrival-time>|<cpu-burst-time>|<num-bursts>|<io-time>")
	for r in range(0,len(task)):
		row = sim[r]
		s=str(task[r]) + "|"
		for r in row:
			s+=str(r)+"|"
		print(s)
	"""
	return task,sim

def add_to_queue(queue, task):
	return numpy.append(queue,task)

def print_ready_queue(queue,task):
	a = "[Q <empty>]"
	if queue.size == 0:
		return a
	a = "[Q"

	for r in queue:
		a += " "+str(task[int(r)])
	a += "]"
	return a


def arrive_to_queue(ready_queue,task,arrival_time,t, cpu):
	for a in range(0,len(task)):
		if arrival_time[a] == t:
			ready_queue = add_to_queue(ready_queue,a)
			removed = ready_queue
			if cpu == ready_queue[0]:
				removed = ready_queue[1:]
			print("time "+str(t)+"ms: Process "+str(task[a])+ " arrived and added to ready queue " + print_ready_queue(removed,task))
	ready_queue = ready_queue.astype('int')
	return ready_queue

def all_arrived (arrival_time,t):
	for a in arrival_time:
		if a > t:
			return False
	return True

def rr (task, data, t_cs, timeslice):

	info = numpy.copy(data)
	arrival_time = info[:,0]
	burst_time = info[:,1]
	num_burst = info[:,2]
	io_time = info [:,3]

	ready_queue = numpy.empty(0) #initiate ready queue
	blocked_queue = numpy.empty(0) #initiate blocked queue
	#TO-Doneed to put completion time here
	completed = (numpy.zeros(len(task))).astype('int')
	completed = numpy.vstack([task,completed])
	#print(completed)

	t = 0
	timer = 0
	prev_timer = 0
	prev = 0
	preempt = 0
	cs = 0

	print ("time "+ str(timer)+"ms: Simulator started for RR " + print_ready_queue(ready_queue,task))
	cpu = -1
	#tasks will be put into the queue
	for n in range(0,len(num_burst)):
		num_burst[n] -= 1

	while (t<timeslice):

		blocked_queue = blocked_queue.astype('int')
		#check blocked
		for blocked_index in blocked_queue:
			if io_time[blocked_index] <= timer:
				blocked_queue = numpy.delete(blocked_queue,[numpy.where(blocked_queue == blocked_index)],None)
				ready_queue = add_to_queue(ready_queue,blocked_index)
				removed = ready_queue
				if (ready_queue.size > 1 and cpu == ready_queue[0]):
					removed = ready_queue[1:]
				print("time "+str(io_time[blocked_index])+"ms: Process "+task[blocked_index]+" completed I/O; added to ready queue " + print_ready_queue(removed,task))
				io_time[blocked_index] = data[blocked_index,3]
				if(ready_queue.size == 1):
					t = 0
		prev_timer = timer

		#running timer
		t+= 1
		timer+=1

		#push tasks into ready queue
		while (prev != timer):
			ready_queue = arrive_to_queue(ready_queue,task,arrival_time,prev,cpu)
			prev += 1

		removed = ready_queue[1:]

		#dump to cpu
		if(ready_queue.size > 0):
			prev_cpu = cpu
			cpu = ready_queue[0]
			#print("prev_cpu = " + str(prev_cpu) + " cpu = " + str(cpu) + " t " + str(t))
			if(t == 1 and cpu != prev_cpu):
				#print("task is now getting assigned")
				#check blocked
				for blocked_index in blocked_queue:
					if io_time[blocked_index] <= timer:
						blocked_queue = numpy.delete(blocked_queue,[numpy.where(blocked_queue == blocked_index)],None)
						ready_queue = add_to_queue(ready_queue,blocked_index)
						removed = ready_queue
						if (ready_queue.size > 1 and cpu == ready_queue[0]):
							removed = ready_queue[1:]
						print("time "+str(io_time[blocked_index])+"ms: Process "+task[blocked_index]+" completed I/O; added to ready queue " + print_ready_queue(removed,task))
						io_time[blocked_index] = data[blocked_index,3]
						if(ready_queue.size == 1):
							t = 1
							timer += 1
				prev_timer = timer

				timer += t_cs/2 
				#check blocked
				for blocked_index in blocked_queue:
					if io_time[blocked_index] < timer:
						blocked_queue = numpy.delete(blocked_queue,[numpy.where(blocked_queue == blocked_index)],None)
						ready_queue = add_to_queue(ready_queue,blocked_index)
						removed = ready_queue
						if (ready_queue.size > 1 and cpu == ready_queue[0]):
							removed = ready_queue[1:]
						print("time "+str(io_time[blocked_index])+"ms: Process "+task[blocked_index]+" completed I/O; added to ready queue " + print_ready_queue(removed,task))
						io_time[blocked_index] = data[blocked_index,3]
						if(ready_queue.size == 1):
							t = 1
							timer += 1
				prev_timer = timer
				
				if (burst_time[cpu] == data[cpu,1]):
					print("time "+str(timer-1)+"ms: Process "+str(task[cpu])+ " started using the CPU "+print_ready_queue(removed,task))
				else:
					print("time "+str(timer-1)+"ms: Process "+str(task[cpu])+ " started using the CPU with "+str(burst_time[cpu])+"ms remaining "+print_ready_queue(removed,task))
				cs += 1 #adding context switch
				#check blocked
				for blocked_index in blocked_queue:
					if io_time[blocked_index] == timer:
						blocked_queue = numpy.delete(blocked_queue,[numpy.where(blocked_queue == blocked_index)],None)
						ready_queue = add_to_queue(ready_queue,blocked_index)
						removed = ready_queue
						if (ready_queue.size > 1 and cpu == ready_queue[0]):
							removed = ready_queue[1:]
						print("time "+str(io_time[blocked_index])+"ms: Process "+task[blocked_index]+" completed I/O; added to ready queue " + print_ready_queue(removed,task))
						io_time[blocked_index] = data[blocked_index,3]
						if(ready_queue.size == 1):
							t = 1
							timer += 1
				prev_timer = timer
		else:
			if  t == timeslice and (ready_queue.size > 0 or blocked_queue.size>0 or not all_arrived(arrival_time,timer)):
				t = 0
			continue;

		#running on cpu
		burst_time[cpu] -= 1

		if burst_time[cpu] == 0:
			if(num_burst[cpu] > 0):
				num_burst[cpu] -= 1
				blocked_queue = add_to_queue(blocked_queue,cpu)
				ready_queue = ready_queue[1:]
				burst_time[cpu] = data[cpu,1]
				
				plural = " bursts"
				if num_burst[cpu] == 0:
					plural = " burst"
				print("time "+str(timer)+"ms: Process "+str(task[cpu])+" completed a CPU burst; "+str(num_burst[cpu]+1)+plural+" to go "+ print_ready_queue(ready_queue,task))
				print("time "+str(timer)+"ms: Process "+str(task[cpu])+" switching out of CPU; will block on I/O until time "+str(timer+io_time[cpu] + t_cs/2)+"ms " + print_ready_queue(ready_queue,task))
				t = 0
				timer+= t_cs/2
				io_time[cpu] = timer+io_time[cpu]
				cpu = -1
				continue;
			else:
				ready_queue = ready_queue[1:] #remove from queue
				print("time "+str(timer)+"ms: Process "+task[cpu]+" terminated "+print_ready_queue(ready_queue,task))
				completed[1][cpu] = timer
				t = 0
				timer+= t_cs/2
				if (ready_queue.size == 0 and blocked_queue.size == 0 and all_arrived(arrival_time,timer)):
					print("time "+str(timer)+"ms: Simulator ended for RR")
					break;

		#preempt
		if t == timeslice:
			if burst_time[cpu] != 0:
				if(cpu == ready_queue[0] and ready_queue.size == 1):
					print("time "+str(timer)+"ms: Time slice expired; no preemption because ready queue is empty [Q <empty>]")
				else:
					ready_queue = ready_queue[1:] #remove from the front
					ready_queue = add_to_queue(ready_queue,cpu) #add to the back of the queue
					print("time "+str(timer)+"ms: Time slice expired; process "+str(task[cpu])+" preempted with "+str(burst_time[cpu])+"ms to go "+print_ready_queue(removed,task))
					preempt += 1
					timer += t_cs/2
					prev_cpu = -1
			if ready_queue.size > 0 or blocked_queue.size>0:
				t = 0
	
	total_burst = 0
	total_round = 0
	total_io = 0
	total_time = 0
	cs_in_io = 0

	for d in data:
		total_burst += d[1]*d[2]
		total_round += d[2]
		total_io += d[3] * (d[2]-1)
		cs_in_io += (t_cs/2)*(d[2]-1)
	
	for c in range(0,len(completed[1])):
		total_time += int(completed[1][c]) - arrival_time[c]

	average_burst = float(total_burst)/float(total_round)
	
	total_ta = total_time - total_io + len(task) * t_cs/2
	average_ta = float(total_ta) / float(total_round)

	total_wait = total_ta - total_burst - cs*t_cs
	average_wait = float(total_wait) / float(total_round)
	
	
	#correct output
	simout = "Algorithm RR\n"
	simout += "-- average CPU burst time: "+"{0:.2f}".format(average_burst)+" ms\n"
	simout += "-- average wait time: " + "{0:.2f}".format(average_wait)+" ms\n"
	simout += "-- average turnaround time: " + "{0:.2f}".format(average_ta)+" ms\n"
	simout += "-- total number of context switches: " + str(cs)+"\n"
	simout += "-- total number of preemptions: "+str(preempt)+"\n"

	return simout



import sys
import string 


class Process:
    def __init__(self, ls):
        # <proc-id>|<initial-arrival-time>|<cpu-burst-time>|<num-bursts>|<io-time>
        self.id = ls[0]
        self.arrivalTime = ls[1]  # initial time that the process arrives 
        self.nextArrTime = ls[1]  # next time should be put in ready queue
        self.CPUburstTime = ls[2]  # burst time
        self.rmBurstTime = ls[2] # initially equal to burst time
        self.totalNumOfBurst = ls[3]   # number of burst 
        self.rmNumOfBurst = ls[3]   # remaining time of burst
        self.iotime = ls[4]     # I/O time
        self.waitTime = []      # time needed to be wait in the ready queue
        self.turnaroundTime = []
        self.stop = 0
        self.arrived = 0
        self.start = 0 # for current process/current part 
        self.backup = ls
        
    def exeBurst(self):
        self.rmNumOfBurst = self.rmNumOfBurst - 1

    def nextArrSet(self, amount):
        self.nextArrTime = amount

    def addWaitTime(self, amount):
        self.waitTime.append(amount)

    def addTadTime(self, amount):
        self.turnaroundTime.append(amount)

    def arriveCPU(self):
        self.arrived = 1

    def startSet(self, amount):
        self.start = amount

    def stopSet(self, amount):
        self.stop = amount

    def rmBstTimeSet(self, amount):
        self.rmBurstTime = amount

    def reset(self):
        self.id = self.backup[0]
        self.arrivalTime = self.backup[1]  # initial time that the process arrives 
        self.nextArrTime = self.backup[1]  # next time should be put in ready queue
        self.CPUburstTime = self.backup[2]  # burst time
        self.rmBurstTime = self.backup[2] # initially equal to burst time
        self.totalNumOfBurst = self.backup[3]   # number of burst 
        self.rmNumOfBurst = self.backup[3]   # remaining time of burst
        self.iotime = self.backup[4]     # I/O time
        self.waitTime = []      # time needed to be wait in the ready queue
        self.turnaroundTime = []
        self.arrived = 0
        self.start = 0 # for current process 
        self.stop = 0


class System:
    def __init__(self, data):
        self.processes = data
        self.ready = []
        self.run = []
        self.block = []
        self.cputime = 0
        self.t_cs = 8
        self.numcswitch = 0
        self.numpreemption = 0
        self.numArrived = 0

    def readyOut(self):
        if (self.ready):
            return ' '.join(self.ready)
        else: 
            return '<empty>'

    def findProcess(self, pid):
        for i in range(len(self.processes)):
            if pid == self.processes[i].id:
                return i
                break

    def reset(self):
        for i in self.processes:
            i.reset()
        self.ready = []
        self.run = []
        self.block = []
        self.cputime = 0
        self.t_cs = 8
        self.numcswitch = 0
        self.numpreemption = 0
        self.numArrived = 0


    def stat(self, simout, algo):
        tburst = 0
        allBstTime = 0
        allTadTime = 0
        allWaitTimeCalc = 0
        for i in self.processes:
            tburst += i.totalNumOfBurst
            allBstTime += i.CPUburstTime*i.totalNumOfBurst
            for j in i.turnaroundTime:
                allTadTime += j
            for j in i.waitTime:
                allWaitTimeCalc += j
        # allWaitTime = allTadTime - allBstTime - self.t_cs*self.numcswitch
        simout.write("Algorithm {}\n".format(algo))
        simout.write("-- average CPU burst time: {0:.2f} ms\n".format(float(allBstTime)/tburst))
        simout.write("-- average wait time: {0:.2f} ms\n".format(float(allWaitTimeCalc)/tburst))
        simout.write("-- average turnaround time: {0:.2f} ms\n".format(float(allTadTime)/tburst))
        simout.write("-- total number of context switches: {}\n".format(self.numcswitch))
        simout.write("-- total number of preemptions: {}\n".format(self.numpreemption))


    ####### ####### ####### ####### ####### #######  FCFS  # ####### ####### ####### ####### ####### #######  FCFS  # ####### ####### ####### ####### ####### #######
    ####### ####### ####### ####### ####### #######  FCFS  # ####### ####### ####### ####### ####### #######  FCFS  # ####### ####### ####### ####### ####### #######
    ####### ####### ####### ####### ####### #######  FCFS  # ####### ####### ####### ####### ####### #######  FCFS  # ####### ####### ####### ####### ####### #######
    ####### ####### ####### ####### ####### #######  FCFS  # ####### ####### ####### ####### ####### #######  FCFS  # ####### ####### ####### ####### ####### #######
    ####### ####### ####### ####### ####### #######  FCFS  # ####### ####### ####### ####### ####### #######  FCFS  # ####### ####### ####### ####### ####### #######
    ####### ####### ####### ####### ####### #######  FCFS  # ####### ####### ####### ####### ####### #######  FCFS  # ####### ####### ####### ####### ####### #######
    ####### ####### ####### ####### ####### #######  FCFS  # ####### ####### ####### ####### ####### #######  FCFS  # ####### ####### ####### ####### ####### #######



    def fcfsReady(self, time):
        currready = []
        for i in self.ready:
            currready.append(self.processes[self.findProcess(i)])
        for i in range(len(self.processes)):
            if (self.processes[i].nextArrTime <= time and \
                self.processes[i].rmNumOfBurst > 0 and \
                self.processes[i].id not in self.ready and \
                self.processes[i].id not in self.run and \
                self.processes[i].id not in self.block):
                currready.append(self.processes[i])
        # sort the currready queue
        currready = sorted(currready, key = lambda x:(x.nextArrTime, x.id))
        self.ready = []
        for i in range(len(currready)):
            self.ready.append(currready[i].id)
            if (self.processes[self.findProcess(currready[i].id)].arrived == 0):
                self.processes[self.findProcess(currready[i].id)].arriveCPU()
                print("time {}ms: Process {} arrived and added to ready queue [Q {}]".format(\
                    currready[i].nextArrTime, currready[i].id, self.readyOut()))

    def fcfsBlock(self, time):
        finish = []
        for i in self.block:
            if (self.processes[self.findProcess(i)].nextArrTime <= time):
                self.ready.append(i)
                # while checking the io, update the queue because we need to find whether the  
                # processes arrive before each ioing process next burst time
                print("time {}ms: Process {} completed I/O; added to ready queue [Q {}]".format(\
                    self.processes[self.findProcess(i)].nextArrTime, i , self.readyOut())) 
                # after finishing the io, print out statements
                self.block.remove(self.processes[self.findProcess(i)].id) # remove it from the io queue
                self.fcfsReady(self.processes[self.findProcess(i)].nextArrTime) 

    def fcfsBlockSort(self):
        finish = []
        for i in self.block:
            finish.append(self.processes[self.findProcess(i)])
        finish = sorted(finish, key = lambda x:(x.nextArrTime, x.id))
        self.block = []
        for i in finish:
            self.block.append(i.id)

    def fcfsAlgo(self):
        print("time {}ms: Simulator started for FCFS [Q {}]".format(0, '<empty>'))
        self.fcfsReady(self.cputime)
        while 1:
            self.fcfsReady(self.cputime)
            if (self.ready):
                current_p = self.ready[0]
                current_p = self.findProcess(current_p)
                self.ready.remove(self.ready[0])
                self.processes[current_p].startSet(self.processes[current_p].nextArrTime)  
                # record start time 
                self.processes[current_p].addWaitTime(self.cputime-self.processes[current_p].nextArrTime) 
                # track wait time 
                self.cputime += self.t_cs/2 # switch in 
                self.numcswitch = self.numcswitch + 1 
                # addup number of switch 
                self.run.append(self.processes[current_p].id) 
                # add to running queue
                print("time {}ms: Process {} started using the CPU [Q {}]".format(\
                    self.cputime, self.processes[current_p].id, self.readyOut())) 
                # if start running, then print out the statement
                self.fcfsReady(self.cputime) 
                self.fcfsBlock(self.cputime)  
                # if any process finishes io when current process is running, fcfs does not require preemption
                self.cputime = self.cputime + self.processes[current_p].CPUburstTime  
                # change cpu time to the time where current processes finishes
                self.processes[current_p].exeBurst()  
                # current process finishes burst for one time
                self.fcfsBlock(self.cputime-1)  
                self.fcfsReady(self.cputime-1)  
                # update the ready queue according to the current time
                # intentionally update using self.cputime-1 to match the output order
                self.processes[current_p].addTadTime(self.cputime + self.t_cs/2 - self.processes[current_p].start) 
                # current time - start time = actual turnaroundTime time
                if (self.processes[current_p].rmNumOfBurst > 0):  
                # if there still nums of burst left 
                    if self.processes[current_p].rmNumOfBurst == 1:
                        print("time {}ms: Process {} completed a CPU burst; {} burst to go [Q {}]".format(\
                        self.cputime, self.processes[current_p].id, self.processes[current_p].rmNumOfBurst, self.readyOut()))
                    else:
                        print("time {}ms: Process {} completed a CPU burst; {} bursts to go [Q {}]".format(\
                        self.cputime, self.processes[current_p].id, self.processes[current_p].rmNumOfBurst, self.readyOut()))
                else: 
                    print("time {}ms: Process {} terminated [Q {}]".format(\
                        self.cputime, self.processes[current_p].id, self.readyOut()))
                if (self.processes[current_p].rmNumOfBurst > 0 and self.processes[current_p].iotime > 0):  # enter io 
                    print("time {}ms: Process {} switching out of CPU; will block on I/O until time {}ms [Q {}]".format(\
                        self.cputime, self.processes[current_p].id, \
                        self.processes[current_p].iotime + self.cputime + self.t_cs/2 , \
                        self.readyOut()))
                    self.fcfsBlock(self.cputime)  
                    self.fcfsReady(self.cputime)  
                    self.block.append(self.processes[current_p].id)
                self.processes[current_p].nextArrSet(self.cputime + self.processes[current_p].iotime + self.t_cs/2)  
                # next up next arrival time for current process
                self.cputime += self.t_cs/2 
                # switch out time for current processes
                self.fcfsReady(self.cputime)
                self.run.remove(self.processes[current_p].id) 
                # remove current processes from running queue
            elif (self.block):
                self.fcfsBlockSort()
                current_p = self.findProcess(self.block[0])
                self.ready.append(self.block[0])
                self.fcfsReady(self.processes[current_p].nextArrTime)
                print("time {}ms: Process {} completed I/O; added to ready queue [Q {}]".format(\
                    self.processes[current_p].nextArrTime, self.processes[current_p].id , self.readyOut()))
                self.cputime = self.processes[current_p].nextArrTime
                self.block.remove(self.block[0])
            else: 
                print("time {}ms: Simulator ended for FCFS".format(self.cputime))
                break


    ####### ####### ####### ####### ####### #######  SRT  # ####### ####### ####### ####### ####### #######  SRT  # ####### ####### ####### ####### ####### #######
    ####### ####### ####### ####### ####### #######  SRT  # ####### ####### ####### ####### ####### #######  SRT  # ####### ####### ####### ####### ####### #######
    ####### ####### ####### ####### ####### #######  SRT  # ####### ####### ####### ####### ####### #######  SRT  # ####### ####### ####### ####### ####### #######
    ####### ####### ####### ####### ####### #######  SRT  # ####### ####### ####### ####### ####### #######  SRT  # ####### ####### ####### ####### ####### #######
    ####### ####### ####### ####### ####### #######  SRT  # ####### ####### ####### ####### ####### #######  SRT  # ####### ####### ####### ####### ####### #######
    ####### ####### ####### ####### ####### #######  SRT  # ####### ####### ####### ####### ####### #######  SRT  # ####### ####### ####### ####### ####### #######
    ####### ####### ####### ####### ####### #######  SRT  # ####### ####### ####### ####### ####### #######  SRT  # ####### ####### ####### ####### ####### #######


    def srtReadySort(self):
        # sort the ready queue based on burst time 
        sortready = []
        for i in self.ready:
            sortready.append(self.processes[self.findProcess(i)])
        sortready = sorted(sortready, key = lambda x:(x.rmBurstTime, x.id))
        self.ready = []
        for i in sortready:
            self.ready.append(i.id)

    def srtBlockSort(self):
        # sort the block queue based on next arrival time
        sortblock = []
        for i in self.block:
            sortblock.append(self.processes[self.findProcess(i)])
        sortblock = sorted(sortblock, key = lambda x:(x.nextArrTime, x.id))
        self.block = []
        for i in sortblock:
            self.block.append(i.id)

    def srtReady(self, time): 
        # update to see if new processes in 
        sortready = sorted(self.processes, key = lambda x:x.id)
        for i in sortready:
            if self.processes[self.findProcess(i.id)].nextArrTime <= time:
                # it first arrived 
                if self.processes[self.findProcess(i.id)].arrived == 0 and \
                i.id not in self.ready and \
                i.id not in self. run and \
                i.id not in self.block:
                    self.numArrived += 1
                    self.processes[self.findProcess(i.id)].arriveCPU()
                    self.ready.append(i.id)
                    self.srtReadySort()
                    print("time {}ms: Process {} arrived and added to ready queue [Q {}]".format(\
                        i.nextArrTime, i.id, self.readyOut()))
                    self.processes[self.findProcess(i.id)].startSet(i.nextArrTime)

    def srtBlock(self, time):
        # output processes that finish io within time
        sortready = []
        for i in self.block:
            if (self.processes[self.findProcess(i)].nextArrTime <= time):
                self.ready.append(i)
                self.srtReadySort()
                print("time {}ms: Process {} completed I/O; added to ready queue [Q {}]".format(\
                    self.processes[self.findProcess(i)].nextArrTime, i , self.readyOut()))
                self.block.remove(i)
                self.processes[self.findProcess(i)].startSet(self.processes[self.findProcess(i)].nextArrTime)

    def srtAlgo(self):
        print("time {}ms: Simulator started for SRT [Q {}]".format(0, '<empty>'))
        self.srtReady(self.cputime)
        while 1:
            self.srtReady(self.cputime)
            self.srtReadySort()
            if (self.ready):
                current_p = self.ready[0]
                current_p = self.findProcess(current_p)
                self.ready.remove(self.ready[0])
                self.processes[current_p].startSet(self.cputime)  
                # record start time 
                if (self.processes[current_p].rmBurstTime == self.processes[current_p].CPUburstTime):
                    self.processes[current_p].addWaitTime(self.cputime-self.processes[current_p].nextArrTime) 
                else: 
                    self.processes[current_p].addWaitTime(self.cputime-self.processes[current_p].stop) 
                # track wait time 
                self.cputime += self.t_cs/2 # switch in 
                self.numcswitch += 1 
                # addup number of switch start
                self.run.append(self.processes[current_p].id)
                # add to running queue
                if self.processes[current_p].rmBurstTime == self.processes[current_p].CPUburstTime:
                    print("time {}ms: Process {} started using the CPU [Q {}]".format(\
                        self.cputime, self.processes[current_p].id, self.readyOut())) 
                else:
                    print("time {}ms: Process {} started using the CPU with {}ms remaining [Q {}]".format(\
                        self.cputime, self.processes[current_p].id, self.processes[current_p].rmBurstTime, self.readyOut()))
                self.srtReady(self.cputime) # update ready queue 
                # flag to see if needs to preempt 
                preempt = 0 
                # check io first see if there are any process that finishes io will preempt 
                self.srtBlockSort()
                pot_p = self.processes[current_p].id
                if self.numArrived != len(self.processes):
                    # not all processes have been arrived 
                    for i in self.block:
                        if self.processes[self.findProcess(i)].nextArrTime <= self.cputime + self.processes[current_p].rmBurstTime and \
                        self.processes[self.findProcess(i)].rmNumOfBurst > 0:
                            if self.processes[self.findProcess(i)].CPUburstTime < self.processes[current_p].rmBurstTime + \
                            self.processes[current_p].start - self.processes[self.findProcess(i)].nextArrTime and i != pot_p:
                                pot_p = i
                                break
                    # get a process possibly will preempt, check if there are any process not arrived yet 
                    # will preempt before that process/ if not get, pot_p is current_p
                    tmpProcess = sorted(self.processes, key = lambda x:(x.arrivalTime, x.CPUburstTime, x.id))
                    for i in tmpProcess:
                        if i.arrived == 0:
                            tmpTime = 0
                            if pot_p == self.processes[current_p].id:
                                # if not find anything io to preempt 
                                tmpTime = self.cputime + self.processes[self.findProcess(pot_p)].rmBurstTime
                            else:
                                tmpTime = self.processes[self.findProcess(pot_p)].nextArrTime
                            if i.nextArrTime <= tmpTime:
                                # if there is a process never executed arrive before i
                                if i.CPUburstTime < self.processes[current_p].rmBurstTime + self.processes[current_p].start - i.nextArrTime:
                                    pot_p = i.id  # update the potential process that will preempt
                                    break
                    if pot_p == self.processes[current_p].id:
                        # no preemption occur, move to lower part to complete the 
                        pass
                    else: 
                        # preemption occur
                        self.numpreemption += 1
                        if self.processes[self.findProcess(pot_p)].arrived == 0:
                            # new process 
                            print("time {}ms: Process {} arrived and will preempt {} [Q {}]".format(\
                                self.processes[self.findProcess(pot_p)].nextArrTime, pot_p, self.processes[current_p].id, self.readyOut()))
                            self.processes[self.findProcess(pot_p)].arriveCPU() # not in ready part
                            self.numArrived += 1
                            self.srtBlock(self.processes[self.findProcess(pot_p)].nextArrTime)
                            self.srtReady(self.processes[self.findProcess(pot_p)].nextArrTime) # update the process to set before the preempt process 
                            # therefore the id will be stored in the self.ready queue 
                            # move the id to the front of the queue
                            self.srtReadySort()
                            self.ready.insert(0 ,pot_p)
                            self.ready.append(self.processes[current_p].id)
                            self.processes[current_p].rmBstTimeSet(\
                                self.processes[current_p].rmBurstTime - \
                                self.processes[self.findProcess(pot_p)].nextArrTime + \
                                self.processes[current_p].start + self.t_cs/2)
                            self.cputime = self.processes[self.findProcess(pot_p)].nextArrTime + self.t_cs/2
                            # start over the queue
                            self.processes[current_p].stopSet(self.processes[self.findProcess(pot_p)].nextArrTime + self.t_cs)
                            continue
                        else: 
                            # block preempt
                            print("time {}ms: Process {} completed I/O and will preempt {} [Q {}]".format(\
                                self.processes[self.findProcess(pot_p)].nextArrTime, pot_p, self.processes[current_p].id, self.readyOut()))
                            self.block.remove(pot_p)
                            self.srtBlock(self.processes[self.findProcess(pot_p)].nextArrTime)
                            self.srtReady(self.processes[self.findProcess(pot_p)].nextArrTime) # update the process to set before the preempt process 
                            self.srtReadySort()
                            self.ready.insert(0,pot_p)
                            self.ready.append(self.processes[current_p].id)
                            self.processes[current_p].rmBstTimeSet(self.processes[current_p].rmBurstTime - \
                                self.processes[self.findProcess(pot_p)].nextArrTime + self.processes[current_p].start + self.t_cs/2)
                            self.cputime = self.processes[self.findProcess(pot_p)].nextArrTime + self.t_cs/2 # and add up switch out time 
                            self.processes[current_p].stopSet(self.processes[self.findProcess(pot_p)].nextArrTime + self.t_cs)
                            continue
                elif self.numArrived == len(self.processes):
                    # all processes have arrived at least once 
                    # only need to check io queue
                    for i in self.block:
                        if self.processes[self.findProcess(i)].nextArrTime <= self.cputime + self.processes[current_p].rmBurstTime and \
                        self.processes[self.findProcess(i)].rmNumOfBurst > 0:
                            if self.processes[self.findProcess(i)].CPUburstTime < self.processes[current_p].rmBurstTime + \
                            self.processes[current_p].start - self.processes[self.findProcess(i)].nextArrTime and i != pot_p:
                                pot_p = i
                                break
                    if pot_p == self.processes[current_p].id:
                        # no preemption occurs
                        pass
                    else:
                        self.numpreemption += 1
                        # preemption from process turn back from i/o queue\
                        print("time {}ms: Process {} completed I/O and will preempt {} [Q {}]".format(\
                            self.processes[self.findProcess(pot_p)].nextArrTime, pot_p, self.processes[current_p].id, self.readyOut()))
                        self.block.remove(pot_p)
                        self.srtBlock(self.processes[self.findProcess(pot_p)].nextArrTime)
                        self.srtReady(self.processes[self.findProcess(pot_p)].nextArrTime) # update the process to set before the preempt process 
                        self.srtReadySort()
                        self.ready.insert(0,pot_p)
                        self.ready.append(self.processes[current_p].id)
                        self.processes[current_p].rmBstTimeSet(self.processes[current_p].rmBurstTime - \
                            self.processes[self.findProcess(pot_p)].nextArrTime + self.processes[current_p].start + self.t_cs/2)
                        self.cputime = self.processes[self.findProcess(pot_p)].nextArrTime + self.t_cs/2 # and add up switch out time 
                        self.processes[current_p].stopSet(self.processes[self.findProcess(pot_p)].nextArrTime + self.t_cs)
                        continue
                # if no preemption occurs, will skip to this part 
                # no preemptions, but still checks if new processing coming in 
                self.srtBlock(self.cputime)
                self.srtReady(self.cputime) 
                self.cputime = self.cputime + self.processes[current_p].rmBurstTime
                self.srtBlock(self.cputime-1)  
                self.srtReady(self.cputime-1)
                # change cpu time to the time where current processes finishes
                self.processes[current_p].exeBurst()  
                # # current process finishes burst for one time
                self.processes[current_p].addTadTime(self.cputime + self.t_cs/2 - self.processes[current_p].nextArrTime) 
                # current time - start time = actual turnaroundTime time
                self.processes[current_p].nextArrSet(self.cputime + self.processes[current_p].iotime + self.t_cs/2)  
                # reset remaining busrt time
                self.processes[current_p].rmBstTimeSet(self.processes[current_p].CPUburstTime)
                if self.processes[current_p].rmNumOfBurst > 0:  
                # if there still nums of burst left 
                    if self.processes[current_p].rmNumOfBurst == 1:
                        print("time {}ms: Process {} completed a CPU burst; {} burst to go [Q {}]".format(\
                            self.cputime, self.processes[current_p].id, self.processes[current_p].rmNumOfBurst, self.readyOut()))
                    else:
                        print("time {}ms: Process {} completed a CPU burst; {} bursts to go [Q {}]".format(\
                            self.cputime, self.processes[current_p].id, self.processes[current_p].rmNumOfBurst, self.readyOut()))
                else: 
                    print("time {}ms: Process {} terminated [Q {}]".format(self.cputime, self.processes[current_p].id, self.readyOut()))
                if self.processes[current_p].rmNumOfBurst > 0 and self.processes[current_p].iotime > 0:  # enter io 
                    print("time {}ms: Process {} switching out of CPU; will block on I/O until time {}ms [Q {}]".format(\
                        self.cputime, self.processes[current_p].id, self.processes[current_p].nextArrTime , self.readyOut()))
                    self.block.append(self.processes[current_p].id)
                self.srtBlock(self.cputime)
                self.srtReady(self.cputime)
                # next up next arrival time for current proces
                self.cputime += self.t_cs/2 
                # switch out time for current processes
                self.srtBlock(self.cputime)
                self.srtReady(self.cputime) 
                self.run.remove(self.processes[current_p].id) 
                # remove current processes from running queue
            elif self.block:
                self.srtBlockSort()
                current_p = self.findProcess(self.block[0])
                self.srtReady(self.processes[current_p].nextArrTime)
                self.ready.append(self.block[0])
                self.srtReadySort()
                print("time {}ms: Process {} completed I/O; added to ready queue [Q {}]".format(\
                    self.processes[current_p].nextArrTime, self.processes[current_p].id , self.readyOut()))
                self.cputime = self.processes[current_p].nextArrTime
                self.block.remove(self.block[0])
            else: 
                print("time {}ms: Simulator ended for SRT".format(self.cputime))
                break

def format(fn):
    # convert txt format 
    # <proc-id>|<initial-arrival-time>|<cpu-burst-time>|<num-bursts>|<io-time>
    # into list format of Process
    lines = []
    with open(fn, 'rb') as f:
        for line in f:
            if (line):  # ignore the empty line 
                if (line[0] != '#' and line[0] != '\n' and line[0] != ' '):  # and comment line
                    line = line.rstrip("\n")   # remove the \n element in each line
                    row = line.split('|')[1:]   # split the element in each line
                    row = map(int, row)   # convert string into int for each element 
                    row.insert(0, line[0])
                    row = Process(row)
                    lines.append(row)   # populate into line matrix
    return lines

if __name__ == '__main__':
    num_cmd = len(sys.argv)
    if num_cmd != 3:
        sys.stderr.write("ERROR: Invalid arguments\nUSAGE: ./a.out <input-file> <stats-output-file>\n")
    	exit(1)
    filename = sys.argv[1]
    outfile = open(sys.argv[2], 'wb')
    name, ext = os.path.splitext(filename)
    if(ext!=".txt"):
		sys.stderr.write("ERROR: Invalid input file format\n")
		exit(1)
    data = format(filename)
    sys = System(data)
    sys.fcfsAlgo()
    sys.stat(outfile,"FCFS")
    print("")
    sys.reset()
    sys.srtAlgo()
    sys.stat(outfile, "SRT")
    task,info = parse_file(filename)
    t_cs = 8 #deletefault
    timeslice = 70
    simout = rr(task,info,t_cs,timeslice)
    outfile.write(simout)
    outfile.close()