#!/usr/bin/env python

import argparse
import subprocess
import sys
import signal
import time
import sudoku

#Definig Parse
parser = argparse.ArgumentParser(description='Sudoku Solver', prog='sudokusolver')

#Add arguments
parser.add_argument('sudokufile', action='store', default="sudoku-5x5.pls", help='Text file with Sudoku problem definition')
parser.add_argument('-o','--output', action='store', default="output.cnf", help='Output file for cnf formula')
parser.add_argument('-e','--encoding', action='store', default="optimized", help='Encoding Method{extended|optimized}')
parser.add_argument('-solve', action='store_true', help='Call SatSolver and pretty print solution (need glucose_1.0 compiled in ./gucose_1.0)')
parser.add_argument('-test', action='store_true', help='Make test')
parser.add_argument('-t','--timeout', action='store', type=int, default="0", help='Test Timeout in milliseconds (default: nolimit)')
parser.add_argument('--version', action='version', version='%(prog)s 1.0')    
args = parser.parse_args()

# Get sudoku file and properties
f = open(args.sudokufile)
order, m = map(int, f.readline().split()[1:3])
n = order / m
sudoku_list = [f.readline().split() for i in range(order)]


# Encode Sudoku to Dimacs CNF Formula
initial_time = time.clock()
s=sudoku.sudoku(args.sudokufile)
if args.encoding == "extended": cnf, decoding_map = s.extended_translate_to_CNF()
elif args.encoding == "optimized": cnf, decoding_map = s.optimized_translate_to_CNF()
else:
	print "Invalid Encoding Option."
	sys.exit()
cnf.print_dimacs(args.output)
encoding_time = time.clock() - initial_time
if args.test: print "Encoding Time:", encoding_time



def print_solution(solution):
	counter = 0
	print "|",
	for var in map(int,solution):
		if var > 0:
			counter += 1
			num = decoding_map.index(var)#falten els prefixed true
			real_value = (num - 1) % order
			if (real_value>9) or (order < 10):print real_value,
			else: print '0'+str(real_value),
			if counter % m == 0:
				if counter % order == 0: print "|\n|",
				else:  print "|",
			if counter % (n*(n*m)) == 0:
				print "--------------------- |\n|",
			if counter >= order**2: break

tout = float(args.timeout)/1000
class TimeoutException(Exception): 
	pass

def timeout(timeout_time, default):
    """Time out Decorators from:
	http://programming-guides.com/python/timeout-a-function
	Usage: @timeout(time,return value)"""

    def timeout_function(f):
	def f2(*args):
	    def timeout_handler(signum, frame):
	        raise TimeoutException()
	    old_handler = signal.signal(signal.SIGALRM, timeout_handler) 
	    signal.setitimer(signal.ITIMER_REAL, timeout_time) # triger alarm in timeout_time seconds
	    try: 
	        retval = f()
	    except TimeoutException:
	        return default
	    finally:
	        signal.signal(signal.SIGALRM, old_handler) 
	    signal.alarm(0)
	    return retval
	return f2
    return timeout_function

@timeout(tout, "timeout")
def execute_glucose():
	output = subprocess.Popen(['./glucose_1.0/glucose.sh',args.output],stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()[0].split()
	if output[1] == 'SATISFIABLE':
		if args.solve: print_solution(output[3:-1])
	else: print "UNSATISFABLE"


# If option -solve or -test: execute SatSolver
if args.solve or args.test:

	if args.output == None:
		print "Argument 'Ouptupt file' (-o, --output) required to print Sudoku solution"
		sys.exit()

	initial_time = time.clock()
	execute_glucose()
	solver_time = time.clock() - initial_time
	if args.test: print "SatSolver Time:", solver_time


