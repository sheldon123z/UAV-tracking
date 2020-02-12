#!/usr/bin/python

# Set icon colors (in CORE) for UAVs and targets

import sys
import time
import argparse
import subprocess
import os

uavs = []
targets = []
filepath = '/tmp/'
curpath = os.path.dirname(os.path.abspath(__file__))
iconpath = curpath + '/icons/uav/'

colors = ['blue', 'yellow', 'green', 'red', 'lime', 'orange', 'pink', 'purple', 'lavender', 'cyan']


#---------------
# Define a CORE node
#---------------
class CORENode():
  def __init__(self, nodeid, colorid):
    self.nodeid = nodeid
    self.colorid = colorid
    self.trackid = -1
    self.oldtrackid = -1;


#---------------
# Read from the filesystem info on which UAV tracks which target
#---------------
def ReadUAVTracking():
  global uavs
  
  for uavnode in uavs:
    fname = 'n%d_track.txt' % uavnode.nodeid
    fname = filepath+fname
    try:
      f = open(fname, 'r')
      line = f.readline()
      f.close()
      uavnode.trackid = int(line)
    except:
      print "Exception: file read error. Ignore..."

    
#---------------
# Update the color of an UAV based on the target it's tracking
#---------------
def UpdateUAVColor(uavnode):
  if uavnode.colorid == -1 or uavnode.colorid >= len(colors):
    color = 'grey'
  else:
    color = colors[uavnode.colorid]

  iconname = color + '_plane.png'
  iconfile = iconpath + iconname
  
  cmd = '/usr/bin/coresendmsg -a 172.16.0.254 NODE NUMBER='
  cmd = cmd + str(uavnode.nodeid) + ' ICON=' + iconfile

  try:
    result = subprocess.check_output([cmd], stderr=subprocess.STDOUT, shell=True)
    sys.stderr.write('{0}'.format(result))
  except:
    print "Exception: vcmd plane icon change error. Ignore..."


#---------------
# Update the color of a target based on whether it's tracked or not
#---------------
def UpdateTargetColor(trgtnode):
  if trgtnode.trackid == -1:
    color = 'grey'
  else:
    color = colors[trgtnode.colorid]

  iconname = color + '_dot.png'
  iconfile = iconpath + iconname
  
  cmd = '/usr/bin/coresendmsg -a 172.16.0.254 NODE NUMBER='
  cmd = cmd + str(trgtnode.nodeid) + ' ICON=' + iconfile

  try:
    result = subprocess.check_output([cmd], stderr=subprocess.STDOUT, shell=True)
    sys.stderr.write('{0}'.format(result))
  except:
    print "Exception: vcmd target icon change error. Ignore..."

    
#---------------
# Assign colors to nodes in CORE
#---------------
def AssignColors():
  global uavs
  global targets

  # Start from a default state
  for trgtnode in targets:
    trgtnode.trackid = -1
      
  # Assign color to all UAVs that track something new
  # Make all UAVs that no longer track something grey
  for uavnode in uavs:
    if uavnode.trackid != uavnode.oldtrackid:
      uavnode.oldtrackid = uavnode.trackid
      # Update the target tracking info and uav color if necessary
      if uavnode.trackid != -1:
        for trgtnode in targets:
          if uavnode.trackid == trgtnode.nodeid:
            trgtnode.trackid = uavnode.nodeid
            uavnode.colorid = trgtnode.colorid
      else:
        uavnode.colorid = -1;
      UpdateUAVColor(uavnode)
      
    # Update target tracking info
    if uavnode.trackid != -1:
      trgtnode = targets[uavnode.colorid]
      trgtnode.trackid = uavnode.nodeid
        
  # Assign color to all targets that are tracked
  # Make all targets not tracked grey
  for trgtnode in targets:
    if trgtnode.trackid != trgtnode.oldtrackid:
      if trgtnode.oldtrackid == -1 or trgtnode.trackid == -1:
          trgtnode.oldtrackid = trgtnode.trackid
          UpdateTargetColor(trgtnode)


#---------------
# main
#---------------
def main():
  global uavs
  global targets
  
  # Get command line inputs 
  parser = argparse.ArgumentParser()
  parser.add_argument('-u','--uav-nodes', dest = 'uav_nodeids', metavar='nodenum',
                      type=int, default = '1', nargs='+', help='UAV node numbers')
  parser.add_argument('-t','--target-nodes', dest = 'trgt_nodeids', metavar='nodenum',
                      type=int, default = '2', nargs='+', help='Target node numbers')
  parser.add_argument('-i','--update_interval', dest = 'interval', metavar='update interval',
                      type=int, default = '1', help='Update Inteval')

  
  # Parse command line options
  args = parser.parse_args()

  nodecnt = 0
  for trgtnodeid in args.trgt_nodeids:
    node = CORENode(int(trgtnodeid), nodecnt)    
    targets.append(node)
    nodecnt += 1
    
  for uavnodeid in args.uav_nodeids:
    node = CORENode(int(uavnodeid), -1)
    uavs.append(node)
    
  msecinterval = float(args.interval) 
  secinterval = msecinterval/1000
  while 1:
    time.sleep(secinterval)
    ReadUAVTracking()    
    AssignColors()

    
if __name__ == '__main__':
  main()
