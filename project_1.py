#!/usr/bin/env python
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

	"""	
	print(info)
	print(data)
	print("ready queue: "+str(ready_queue))
	print("blocked queue: " + str(blocked_queue))
	"""
	print(completed)
	
	total_burst = 0
	total_round = 0
	total_io = 0
	total_time = 0

	for d in data:
		total_burst += d[1]*d[2]
		total_round += d[2]
		total_io += d[3] * (d[2]-1)
	
	for c in completed[1]:
		total_time += int(c)

	for a in arrival_time:
		total_time -= a

	total_cs = (cs+preempt)*(t_cs/2)
	average_burst = float(total_burst)/float(total_round)

	print(total_io)
	total_ta = total_time - total_io 
	average_ta = float(total_ta) / float(total_round)
	

	print("total cs time: "+str(total_cs))
	print ("total time: "+str(total_time))
	print("average turnaround: " + str(round(average_ta,2)))
	#correct output
	print("average burst: "+str(round(average_burst,2)))
	print ("context swith: " + str(cs))
	print("preempt: "+str(preempt))



if __name__ == '__main__':
	num_cmd = len(sys.argv)
	if(num_cmd<2):
		sys.stderr.write("ERROR: Invalid arguments\n" + "USAGE: ./a.out <input-file> <stats-output-file>\n")
		exit(1)
	filename = sys.argv[-1]
	name, ext = os.path.splitext(filename)
	if(ext!=".txt"):
		sys.stderr.write("ERROR: Invalid input file format\n")
		exit(1)
	task,info = parse_file(filename)
	t_cs = 8 #deletefault
	timeslice = 70

	rr(task,info,t_cs,timeslice)