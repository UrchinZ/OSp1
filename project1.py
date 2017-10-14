#!/usr/bin/env python
import sys
import numpy
import string

def format_file(filename):
	f = open(filename)
	task = []
	row  = numpy.empty(4)
	sim = numpy.empty(4)
	for line in f:
		if line[0] == '#':
			continue
		n = 0
		for v in line.split('|'):
			if n == 0:
				task.append(v)
			else:
				row[n-1] = v
			n=n+1
		sim = numpy.vstack([sim, row])
	f.close()
	sim = numpy.delete(sim, (0), axis=0)
	sim = sim.astype('int')
	print("<proc-id>|<initial-arrival-time>|<cpu-burst-time>|<num-bursts>|<io-time>")
	for r in range(0,len(task)):
		row = sim[r]
		s=str(task[r]) + "|"
		for r in row:
			s+=str(r)+"|"
		print(s)
	return sim

if __name__ == '__main__':
	print("This is project 1")
	num_cmd = len(sys.argv)
	filename = sys.argv[-1]
	info = format_file(filename)


