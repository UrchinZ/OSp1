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
                    print (self.cputime, self.processes[current_p].stop)
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
                        if self.processes[self.findProcess(i)].nextArrTime <= self.cputime + self.processes[current_p].rmBurstTime and self.processes[self.findProcess(i)].rmNumOfBurst > 0:
                            if self.processes[self.findProcess(i)].CPUburstTime < self.processes[current_p].rmBurstTime + self.processes[current_p].start - self.processes[self.findProcess(i)].nextArrTime and i != pot_p:
                                pot_p = i
                                break
                    # get a process possibly will preempt, check if there are any process not arrived yet will preempt before that process/ if not get, pot_p is current_p
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
                            print("time {}ms: Process {} arrived and will preempt {} [Q {}]".format(self.processes[self.findProcess(pot_p)].nextArrTime, pot_p, self.processes[current_p].id, self.readyOut()))
                            self.processes[self.findProcess(pot_p)].arriveCPU() # not in ready part
                            self.numArrived += 1
                            self.srtBlock(self.processes[self.findProcess(pot_p)].nextArrTime)
                            self.srtReady(self.processes[self.findProcess(pot_p)].nextArrTime) # update the process to set before the preempt process 
                            # therefore the id will be stored in the self.ready queue 
                            # move the id to the front of the queue
                            self.srtReadySort()
                            self.ready.insert(0 ,pot_p)
                            self.ready.append(self.processes[current_p].id)
                            self.processes[current_p].rmBstTimeSet(self.processes[current_p].rmBurstTime - self.processes[self.findProcess(pot_p)].nextArrTime + self.processes[current_p].start + self.t_cs/2)
                            self.cputime = self.processes[self.findProcess(pot_p)].nextArrTime + self.t_cs/2
                            # start over the queue
                            self.processes[current_p].stopSet(self.processes[self.findProcess(pot_p)].nextArrTime + self.t_cs)
                            continue
                        else: 
                            # block preempt
                            print("time {}ms: Process {} completed I/O and will preempt {} [Q {}]".format(self.processes[self.findProcess(pot_p)].nextArrTime, pot_p, self.processes[current_p].id, self.readyOut()))
                            self.block.remove(pot_p)
                            self.srtBlock(self.processes[self.findProcess(pot_p)].nextArrTime)
                            self.srtReady(self.processes[self.findProcess(pot_p)].nextArrTime) # update the process to set before the preempt process 
                            self.srtReadySort()
                            self.ready.insert(0,pot_p)
                            self.ready.append(self.processes[current_p].id)
                            self.processes[current_p].rmBstTimeSet(self.processes[current_p].rmBurstTime - self.processes[self.findProcess(pot_p)].nextArrTime + self.processes[current_p].start + self.t_cs/2)
                            self.cputime = self.processes[self.findProcess(pot_p)].nextArrTime + self.t_cs/2 # and add up switch out time 
                            self.processes[current_p].stopSet(self.processes[self.findProcess(pot_p)].nextArrTime + self.t_cs)
                            continue
                elif self.numArrived == len(self.processes):
                    # all processes have arrived at least once 
                    # only need to check io queue
                    for i in self.block:
                        if self.processes[self.findProcess(i)].nextArrTime <= self.cputime + self.processes[current_p].rmBurstTime and self.processes[self.findProcess(i)].rmNumOfBurst > 0:
                            if self.processes[self.findProcess(i)].CPUburstTime < self.processes[current_p].rmBurstTime + self.processes[current_p].start - self.processes[self.findProcess(i)].nextArrTime and i != pot_p:
                                pot_p = i
                                break
                    if pot_p == self.processes[current_p].id:
                        # no preemption occurs
                        pass
                    else:
                        self.numpreemption += 1
                        # preemption from process turn back from i/o queue\
                        print("time {}ms: Process {} completed I/O and will preempt {} [Q {}]".format(self.processes[self.findProcess(pot_p)].nextArrTime, pot_p, self.processes[current_p].id, self.readyOut()))
                        self.block.remove(pot_p)
                        self.srtBlock(self.processes[self.findProcess(pot_p)].nextArrTime)
                        self.srtReady(self.processes[self.findProcess(pot_p)].nextArrTime) # update the process to set before the preempt process 
                        self.srtReadySort()
                        self.ready.insert(0,pot_p)
                        self.ready.append(self.processes[current_p].id)
                        self.processes[current_p].rmBstTimeSet(self.processes[current_p].rmBurstTime - self.processes[self.findProcess(pot_p)].nextArrTime + self.processes[current_p].start + self.t_cs/2)
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
                        print("time {}ms: Process {} completed a CPU burst; {} burst to go [Q {}]".format(self.cputime, self.processes[current_p].id, self.processes[current_p].rmNumOfBurst, self.readyOut()))
                    else:
                        print("time {}ms: Process {} completed a CPU burst; {} bursts to go [Q {}]".format(self.cputime, self.processes[current_p].id, self.processes[current_p].rmNumOfBurst, self.readyOut()))
                else: 
                    print("time {}ms: Process {} terminated [Q {}]".format(self.cputime, self.processes[current_p].id, self.readyOut()))
                if self.processes[current_p].rmNumOfBurst > 0 and self.processes[current_p].iotime > 0:  # enter io 
                    print("time {}ms: Process {} switching out of CPU; will block on I/O until time {}ms [Q {}]".format(self.cputime, self.processes[current_p].id, self.processes[current_p].nextArrTime , self.readyOut()))
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
                print("time {}ms: Process {} completed I/O; added to ready queue [Q {}]".format(self.processes[current_p].nextArrTime, self.processes[current_p].id , self.readyOut()))
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
    else:
        filename = sys.argv[1]
        outfile = open(sys.argv[2], 'wb')
        data = format(filename)
        sys = System(data)
        sys.fcfsAlgo()
        sys.stat(outfile,"FCFS")
        print("")
        sys.reset()
        sys.srtAlgo()
        sys.stat(outfile, "SRT")
        outfile.close()