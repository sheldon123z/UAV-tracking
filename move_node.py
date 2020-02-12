#!/usr/bin/python

# Advance a vehicle towards a target and then move in a circle
# pattern around it

import sys
import math
import time
import subprocess

filepath = '/tmp/'


#---------------
# Calculate the distance between two points (on a map)
#---------------
def Distance(x1, y1, x2, y2):
  return math.sqrt(math.pow(y2-y1, 2) + math.pow(x2-x1, 2))


#---------------
# Find the new position as a vehicle moves towards a waypoint
#---------------
def MoveToWaypoint(xold, yold, xwypt, ywypt, speed, duration):
  movedist = speed * duration
  totaldist = Distance(xold, yold, xwypt, ywypt)
  ratio = movedist/totaldist

  xnew = xold + (xwypt-xold)*ratio
  ynew = yold + (ywypt-yold)*ratio

  return xnew, ynew


#---------------
# Move a node clock-wise around a circle
#---------------
def MoveOnCircle(xnode, ynode, xcenter, ycenter, radius, distance):
  posangle = math.atan2(ynode-ycenter, xnode-xcenter)
  moveangle = -distance/radius # That's negative for counter-clockwise,
                               # but in CORE Y coordinates are reversed...
  xnew = xcenter + radius*math.cos(posangle-moveangle)
  ynew = ycenter + radius*math.sin(posangle-moveangle)
    
  return xnew, ynew
  

#---------------
# Move the vehicle towards the target if it's far away,
# or on a circle around the target if it's close enough
#---------------
def MoveVehicle(xold, yold, xtrgt, ytrgt, rad, speed, duration):
  # Check whether the vehicle is outside the circle around the target  
  trgtdist = Distance(xold, yold, xtrgt, ytrgt)
  movedist = speed * duration
  if trgtdist >= rad:
    # Check if the vehicle would still be outside the circle after moving
    if trgtdist - movedist >= rad:
      xnew, ynew = MoveToWaypoint(xold, yold, xtrgt, ytrgt, speed, duration)
      return xnew, ynew
    else:
      # Moving to the circle and then moving on the circle for the rest of
      # the distance
      if trgtdist == 0:      # Special case: vehicle is collocated with 
        return xold, yold    # the target and radius is zero
      
      tocircledist = trgtdist - rad
      circledist = movedist - tocircledist
      ratio = tocircledist/trgtdist
      xcircle = xold + (xtrgt-xold)*ratio
      ycircle = yold + (ytrgt-yold)*ratio

      xnew, ynew = MoveOnCircle(xcircle, ycircle, xtrgt, ytrgt, rad, circledist)
      return xnew, ynew
  else:
    # Vehicle is inside the circle; needs to move away from the target to
    # join the circle

    # Find the waypoint on the circle in straight move
    tocircledist = rad - trgtdist
    if trgtdist == 0:   #Special case: vehicle is collocated with target
      xcircle = xtrgt+rad
      ycircle = ytrgt
    else:
      ratio = rad/trgtdist
      xcircle = xtrgt + (xold-xtrgt)*ratio
      ycircle = ytrgt + (yold-ytrgt)*ratio

    # Check if the vehicle would still be outside the circle after moving 
    if movedist + trgtdist <= rad:
      # Moving in a straight line inside the circle
      xnew, ynew = MoveToWaypoint(xold, yold, xcircle, ycircle, speed, duration)
      return xnew, ynew
    else:
      # Moving straight to the circle until hitting the circle waypoint and then
      # moving on the circle from there for the rest of the distance 
      circledist = movedist - tocircledist
      xnew, ynew = MoveOnCircle(xcircle, ycircle, xtrgt, ytrgt, rad, circledist)
      return xnew, ynew

#---------------
# main
#---------------
def main():
  # Get command line inputs 
  if len(sys.argv) >= 7:
    node  = int(sys.argv[1])
    xuav  = int(sys.argv[2])
    yuav  = int(sys.argv[3])
    rad   = int(sys.argv[4])
    speed = float(sys.argv[5])
    msecduration  = float(sys.argv[6])
    duration = msecduration/1000
  else:
    print 'move_node.py nodenum xuav yuav radius speed duration(msec)\n'
    sys.exit()

  fname = 'n%d_wypt.txt' % node
  fname = filepath + fname
  
  while 1:
    time.sleep(duration)
    try:
      f = open(fname, 'r')
      line = f.readline()
      f.close()
      xtrgtstr, ytrgtstr = line.split(" ")
      xtrgt = int(xtrgtstr)
      ytrgt = int(ytrgtstr)
    
      xuav, yuav = MoveVehicle(xuav, yuav, xtrgt, ytrgt, rad, speed, duration)

      print "here", node, xuav, yuav
      
      cmd = '/usr/bin/coresendmsg -a 172.16.0.254 NODE NUMBER='+str(node)+' X_POSITION='+str(int(xuav))+' Y_POSITION='+str(int(yuav))
      result = subprocess.check_output([cmd], stderr=subprocess.STDOUT, shell=True)
      sys.stderr.write('{0}'.format(result))
    except:
      print "Exception: file read error. Ignore..."
      
if __name__ == '__main__':
  main()
