# This module tracks the latency from when targets nodes are placed in range of the uav nodes to when the last uav node tracks its target node. 
# The goal is to have all uav nodes track unique targets. But, the program should still complete if this does not happen. # The program creates an output log stored in "/tmp/norm_latency_avg.log"


#!/user/bin/python

import time
import datetime
import sys
import subprocess
import argparse


targets = []
uavs = []
starttime = []
stoptime = []
pairing = []
filepath = '/tmp/'

nodepair = {}


def checkUnique(nodepairdict):

	# Check whether a group of uavs all pick unique targets

    print "Node Pair Dict: %s" % nodepairdict

    isUnique = True
    check = {}
    
    for key,value in nodepairdict.items():
        if value not in check.keys():
            check[value]=[key]
        else:
            check[value].append(key)
            isUnique = False

    print "Check Dict: %s" % check
    print "isUnique: %s" % check

    return isUnique
        


def startTimer():

	# Begin timer to start tracking latency for run

    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')
    starttime.append((ts,st))
    xuav = 200
    yuav = 100

	# Move targets within range of uavs	
	
    for i in range(1,len(targets)+1):
        #print 'I: ', i, '\tT: ', targets[i-1]
        if (i % 2) == 0:
            cmd = '/usr/local/sbin/coresendmsg -a 172.16.0.254 node number='+str(targets[i-1])+' xpos='+str(xuav+200)+' ypos='+str(yuav+(i/2-1)*150)
        else:
            cmd = '/usr/local/sbin/coresendmsg -a 172.16.0.254 node number='+str(targets[i-1])+' xpos='+str(xuav)+' ypos='+str(yuav+((i-1)/2)*150)

            #print 'cmd: ', cmd
      
        try:
            result = subprocess.check_output([cmd], stderr=subprocess.STDOUT, shell=True)
            sys.stderr.write('{0}'.format(result))
        except:
            print "Exception: Calculate(): vcmd target move change error. Ignore..."
    

def stopTimer():

	# Stop timer and record latency for run

    global nodepair
    
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')
    stoptime.append((ts,st))
    pairing.append(nodepair)
    nodepair = {}
    
    xuav = 1300
    yuav = 100

	# Wait 5 seconds

    time.sleep(5)

	# Move targets out of range of uavs
  
    for i in range(1,len(targets)+1):
        
        if (i % 2) == 0:
            cmd = '/usr/local/sbin/coresendmsg -a 172.16.0.254 node number='+str(targets[i-1])+' xpos='+str(xuav+100)+' ypos='+str(yuav+(i/2-1)*100)
        else:
            cmd = '/usr/local/sbin/coresendmsg -a 172.16.0.254 node number='+str(targets[i-1])+' xpos='+str(xuav)+' ypos='+str(yuav+((i-1)/2)*100)
      
        try:
            result = subprocess.check_output([cmd], stderr=subprocess.STDOUT, shell=True)
            sys.stderr.write('{0}'.format(result))
        except:
            print "Exception: Calculate(): vcmd target move change error. Ignore..."

	# Wait 5 seconds

    time.sleep(5)


def formatTime():

    # Format output latency log file

    numUnique = 0
    numDuplicate = 0


    fpath = filepath + '/norm_latency_avg.log'
    f=open(fpath, 'w+')

    f.write("\nFIND AVERAGE TIME for %d RUNS:\n\n" % numloops)
    
    tsum = 0
        
    for i in range(len(starttime)):
        f.write("\t---------- RUNS %d ----------\n" % (i+1))
        tdiff = stoptime[i][0]-starttime[i][0]
        tsum = tsum + tdiff
        f.write("\tLatency:\t%.5f seconds\n" % tdiff)
        f.write("\tStart Time:\t%s\n" % starttime[i][1])
        f.write("\tStop Time:\t%s\n" % stoptime[i][1])
        f.write("\tNode Pairing: %s\n" % pairing[i])
        if checkUnique(pairing[i]):
	    f.write("\tAll nodes have unique target! :)\n\n")
            numUnique += 1
        else:
            f.write("\tSome nodes have the same target! :(\n\n")
            numDuplicate += 1

    tavg = tsum/len(starttime)

    f.write("----------------------------------------------------------\n")

    f.write("\n\nAVERAGE TIME for %s RUNS:\t%.5f seconds\n\n" % (numloops,tavg))
    f.write("Number of times node-target pairings had all unique targets:\t%s\n" % numUnique)
    f.write("Number of times node-target pairings had duplicate targets:\t\t%s\n" % numDuplicate)

    print 'AVERAGE TIME for ', numloops, ' RUNS:\t', tavg , ' seconds'
    print 'Number of times node-target pairings had all unique targets: \t', numUnique
    print 'Number of times node-target pairings had duplicate targets: \t\t', numDuplicate

    f.close()


def main():

    global uavs
    global targets
    global numloops
    global nodepair

    # Get command line inputs
    parser = argparse.ArgumentParser()
    parser.add_argument('-u','--uav-nodes', dest = 'uav_nodeids', metavar='nodenum',
                      type=int, default = '1', nargs='+', help='UAV node numbers')
    parser.add_argument('-t','--target-nodes', dest = 'trgt_nodeids', metavar='nodenum',
                      type=int, default = '2', nargs='+', help='Target node numbers')

    parser.add_argument('-l', '--num-of-loops', dest = 'num_loops', metavar='loopnum',
                        type=int, default = '2', help='Number of loops')

    # Parse command line options
    args = parser.parse_args()

    numloops = args.num_loops

    # Populate the target list
    for trgtnodeid in args.trgt_nodeids:
        targets.append(trgtnodeid)

    # Populate the uav list    
    for uavnodeid in args.uav_nodeids:
        uavs.append(uavnodeid)
    
    # Calculate 
    
    timercount = 1
    timerstate = 0

    time.sleep(10)
	
    # Check if you should start and stop timer
    while timercount <= numloops:
        if timerstate == 0:
            startTimer()
            timerstate = 1

        if timerstate == 1:
            
            foundall = 1

            for uavnode in uavs:
                fname = 'n%d_track.txt' % uavnode
                fname = filepath+fname
                try:
                  f = open(fname, 'r')
                  line = f.readline()
                  f.close()
                  time.sleep(0.1)
                  trackid = int(line)

                  nodepair[uavnode] = trackid
                  
                  if trackid < 0:
                      foundall = 0
                      
                except:
                  print "Exception: file read error. Ignore..."

            #print "Foundall: ", foundall

            if foundall == 1:
                #percentage = timercount/(numloops*1.00) * 100
                print "Round %d of %d Completed" % (timercount, numloops)
                stopTimer()
                timercount = timercount + 1
                timerstate = 0
    
	# Format log file 
	
    formatTime()

	# Wait 10 seconds

    time.sleep(10)

if __name__ == '__main__':
    main()


