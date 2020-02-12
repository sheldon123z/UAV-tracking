#!/usr/bin/python

# Set target (waypoint) positions for UAVs

import sys
import struct
import socket
import math
import time
import argparse
import glob
import subprocess
import threading
import datetime

uavs = []
targets = []
mynodeseq = 0
protocol = 'none'
mcastaddr = '235.1.1.1'
port = 9100
ttl = 64

filepath = '/tmp'
nodepath = ''

thrdlock = threading.Lock()



#---------------
# Define a CORE node
#---------------
class CORENode():
  def __init__(self, nodeid, x, y, track_nodeid):
    self.nodeid = nodeid
    self.x = x
    self.y = y
    self.trackid = track_nodeid
    self.oldtrackid = track_nodeid;


    
#---------------
# Thread that receives UDP Advertisements
#---------------
class ReceiveUDPThread(threading.Thread):    
  def __init__(self):
    threading.Thread.__init__(self)
    
  def run(self):
    ReceiveUDP()
    
      
#---------------
# Calculate the distance between two modes (on a map)
#---------------
def Distance(node1, node2):
  return math.sqrt(math.pow(node2.y-node1.y, 2) + math.pow(node2.x-node1.x, 2))


#---------------
# Redeploy a UAV back to its original position
#---------------
def RedeployUAV(uavnode):   
  origposfile = filepath + '/n' + str(uavnode.nodeid) + '_orig_wypt.txt'
  posfile = filepath + '/n' + str(uavnode.nodeid) + '_wypt.txt'
  cmd = 'cp ' + origposfile + ' ' + posfile

  try:
    result = subprocess.check_output([cmd], stderr=subprocess.STDOUT, shell=True)
    sys.stderr.write('{0}'.format(result))
  except:
    print "Exception: copy waypoint from original position file. Ignore..."


#---------------
# Write the target tracked to the file system so coloring
# can be updated if necessary
#---------------
def RecordTarget(uavnode):
  fname = '/n%d_track.txt' % uavnode.nodeid
  fname = filepath + fname
  line = str(uavnode.trackid)
  try:
    f = open(fname, 'w')
    f.write(line) 
    f.close()
  except:
    print "Exception: track file write error. Ignore..."


#---------------
# Advertise the target being tracked over UDP
#---------------
def AdvertiseUDP(uavnodeid, trgtnodeid):
  addrinfo = socket.getaddrinfo(mcastaddr, None)[0]
  sk = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
  ttl_bin = struct.pack('@i', ttl)
  sk.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)

  buf = str(uavnodeid) + ' ' + str(trgtnodeid)
  sk.sendto(buf, (addrinfo[4][0], port))


#---------------
# Receive and parse UDP advertisments
#---------------
def ReceiveUDP():
  addrinfo = socket.getaddrinfo(mcastaddr, None)[0]
  sk = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
  sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

  # Bind
  sk.bind(('', port))

  # Join group
  group_bin = socket.inet_pton(addrinfo[0], addrinfo[4][0])
  mreq = group_bin + struct.pack('=I', socket.INADDR_ANY)
  sk.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

  while 1:
    buf, sender = sk.recvfrom(1500)
    uavidstr, trgtidstr = buf.split(" ")        
    uavnodeid, trgtnodeid = int(uavidstr), int(trgtidstr)

    # Update tracking info for other UAVs
    uavnode = uavs[mynodeseq]
    if uavnode.nodeid != uavnodeid:
      UpdateTracking(uavnodeid, trgtnodeid)

      
#---------------
# Update tracking info based on a received advertisement
#---------------
def UpdateTracking(uavnodeid, trgtnodeid):
  # Update corresponding UAV node structure with tracking info
  if protocol == 'udp':
    thrdlock.acquire()
  
  for uavnode in uavs:
    if uavnode.nodeid == uavnodeid:
      uavnode.trackid = trgtnodeid
      
  if protocol == 'udp':
    thrdlock.release()

  
#---------------
# Update waypoints for targets tracked, or track new targets
#---------------
def TrackTargets(covered_zone, track_range):
  #print 'Track Targets'
  uavnode = uavs[mynodeseq]
  uavnode.trackid = -1
  updatewypt = 0

  commsflag = 0
  if protocol == 'udp':
    commsflag = 1
    
  for trgtnode in targets:    
    # If this UAV was tracking this target before and it's still
    # in range then it should keep it.
    # Update waypoint to the new position of the target
    if uavnode.oldtrackid == trgtnode.nodeid and trgtnode.x <= covered_zone:
      if Distance(uavnode, trgtnode) <= track_range:
        # Keep the current tracking; no need to change
        # unless the track goes out of range
        #print 'Keep the current tracking; no need to change ', trgtnode.nodeid
        uavnode.trackid = trgtnode.nodeid
        updatewypt = 1

    # If this UAV was not tracking any target and finds one in range    
    if uavnode.oldtrackid == -1 and trgtnode.x <= covered_zone:
      if Distance(uavnode, trgtnode) <= track_range:
        # If we're using , check if the target is being tracked by another UAV
        if commsflag == 1:
          trackflag = 0
          for uavnodetmp in uavs:
            if uavnodetmp.trackid == trgtnode.nodeid or \
               (uavnodetmp.trackid == 0 and uavnodetmp.oldtrackid == trgtnode.nodeid):
              #print 'Target ', trgtnode.nodeid, ' is being tracked already'
              trackflag = 1
            
        if commsflag == 0 or trackflag == 0: 
          # UAV node should track this target
          #print 'UAV node should track this target ', trgtnode.nodeid
          uavnode.trackid = trgtnode.nodeid
          updatewypt = 1
        
    if updatewypt == 1:
      # Update waypoint for UAV node
      updatewypt = 0
      fname = '/n%d_wypt.txt' % uavnode.nodeid
      fname = filepath + fname
      line = str(int(trgtnode.x)) + " " + str(int(trgtnode.y))
      try:
        f = open(fname, 'w')
        f.write(line) 
        f.close()
      except:
        print "Exception: position file write error. Ignore..."

  # Reset tracking info for other UAVs if we're using comms
  if commsflag == 1:
    for uavnodetmp in uavs:
      if uavnodetmp.nodeid != uavnode.nodeid:
        uavnodetmp.oldtrackid = uavnodetmp.trackid
        uavnodetmp.trackid = 0
          
  # Advertise target being tracked if using comms 
  if protocol == 'udp':
    AdvertiseUDP(uavnode.nodeid, uavnode.trackid)
    
  # Record the target tracked for displaying proper colors
  # Re-deploy UAV if it's not track anything
  if uavnode.trackid != uavnode.oldtrackid:
    uavnode.oldtrackid = uavnode.trackid
    RecordTarget(uavnode)
    if uavnode.trackid == -1:
      RedeployUAV(uavnode)

#---------------
# main
#---------------
def main():
  global uavs
  global targets
  global protocol
  global nodepath
  global mynodeseq
  
  # Get command line inputs 
  parser = argparse.ArgumentParser()
  parser.add_argument('-my','--my-id', dest = 'uav_id', metavar='my id',
                      type=int, default = '1', help='My Node ID')
  parser.add_argument('-u','--uav-nodes', dest = 'uav_nodeids', metavar='nodenum',
                      type=int, default = '1', nargs='+', help='UAV node numbers')
  parser.add_argument('-t','--target-nodes', dest = 'trgt_nodeids', metavar='nodenum',
                      type=int, default = '2', nargs='+', help='Target node numbers')
  parser.add_argument('-c','--covered-zone', dest = 'covered_zone', metavar='covered zone',
                      type=int, default = '1200', help='UAV covered zone limit on X axis')
  parser.add_argument('-r','--track_range', dest = 'track_range', metavar='track range',
                      type=int, default = '600', help='UAV tracking range')
  parser.add_argument('-i','--update_interval', dest = 'interval', metavar='update interval',
                      type=int, default = '1', help='Update Inteval')
  parser.add_argument('-p','--protocol', dest = 'protocol', metavar='comms protocol',
                      type=str, default = 'none', help='Comms Protocol')

  
  # Parse command line options
  args = parser.parse_args()

  protocol = args.protocol
  
  # Populate the targets list
  for trgtnodeid in args.trgt_nodeids:
    node = CORENode(int(trgtnodeid), 0, 0, 0)
    targets.append(node)

  # Populate the uavs list and initialize UAV positions and original waypoints in CORE
  nodecnt = 0
  mynodeseq = -1
  for uavnodeid in args.uav_nodeids:
    node = CORENode(int(uavnodeid), 0, 0, -1)
    uavs.append(node)
    if args.uav_id == uavnodeid:
      mynodeseq = nodecnt
      RedeployUAV(node)
      RecordTarget(node)
      
    nodecnt += 1

  if mynodeseq == -1:
    print 'Error: my id needs to be in the list of UAV IDs'
    sys.exit
    
  corepath = '/tmp/pycore.*/'
  nodepath = glob.glob(corepath)[0]
  msecinterval = float(args.interval)
  secinterval = msecinterval/1000

  if protocol == 'udp':
    # Create UDP receiving thread
    recvthrd = ReceiveUDPThread()
    recvthrd.start()
        
  # Start tracking targets
  while 1:
    time.sleep(secinterval)
    
    # Read all target node positions
    for trgtnode in targets:
      fname = 'n%d.xy' % trgtnode.nodeid
      fname = nodepath+fname    
      try:
        f = open(fname, 'r')
        line = f.readline()
        f.close()
        xstr, ystr = line.split(" ")
        trgtnode.x, trgtnode.y = float(xstr), float(ystr)
      except:
        print "Exception: file read error. Ignore..."

    # Read all UAV node positions
    for uavnode in uavs:
      fname = 'n%d.xy' % uavnode.nodeid
      fname = nodepath+fname
      try:
        f = open(fname, 'r')
        line = f.readline()
        f.close()
        xstr, ystr = line.split(" ")        
        uavnode.x, uavnode.y = float(xstr), float(ystr)
      except:
        print "Exception: file read error. Ignore..."

    if protocol == 'udp':    
      thrdlock.acquire()
    
    TrackTargets(args.covered_zone, args.track_range)

    if protocol == 'udp':
      thrdlock.release()


if __name__ == '__main__':
  main()
