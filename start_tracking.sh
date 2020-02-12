#!/bin/bash

coredir=$(ls /tmp | grep pycore)
filedir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

vcmd -c /tmp/$coredir/n1 -- killall track_target.py
vcmd -c /tmp/$coredir/n2 -- killall track_target.py
vcmd -c /tmp/$coredir/n3 -- killall track_target.py
vcmd -c /tmp/$coredir/n4 -- killall track_target.py
vcmd -c /tmp/$coredir/n6 -- killall track_target.py
vcmd -c /tmp/$coredir/n7 -- killall track_target.py
vcmd -c /tmp/$coredir/n8 -- killall track_target.py
vcmd -c /tmp/$coredir/n9 -- killall track_target.py


vcmd -c /tmp/$coredir/n1 -- $filedir/track_target.py -my 1 -u 1 2 3 4 6 7 8 9 -t 11 12 13 14 16 17 18 19 -i 500 -p $1 > /tmp/track_n1.log 2>&1 &
vcmd -c /tmp/$coredir/n2 -- $filedir/track_target.py -my 2 -u 1 2 3 4 6 7 8 9 -t 11 12 13 14 16 17 18 19 -i 500 -p $1 > /tmp/track_n1.log 2>&1 &
vcmd -c /tmp/$coredir/n3 -- $filedir/track_target.py -my 3 -u 1 2 3 4 6 7 8 9 -t 11 12 13 14 16 17 18 19 -i 500 -p $1 > /tmp/track_n1.log 2>&1 &
vcmd -c /tmp/$coredir/n4 -- $filedir/track_target.py -my 4 -u 1 2 3 4 6 7 8 9 -t 11 12 13 14 16 17 18 19 -i 500 -p $1 > /tmp/track_n1.log 2>&1 &
vcmd -c /tmp/$coredir/n6 -- $filedir/track_target.py -my 6 -u 1 2 3 4 6 7 8 9 -t 11 12 13 14 16 17 18 19 -i 500 -p $1 > /tmp/track_n1.log 2>&1 &
vcmd -c /tmp/$coredir/n7 -- $filedir/track_target.py -my 7 -u 1 2 3 4 6 7 8 9 -t 11 12 13 14 16 17 18 19 -i 500 -p $1 > /tmp/track_n1.log 2>&1 &
vcmd -c /tmp/$coredir/n8 -- $filedir/track_target.py -my 8 -u 1 2 3 4 6 7 8 9 -t 11 12 13 14 16 17 18 19 -i 500 -p $1 > /tmp/track_n1.log 2>&1 &
vcmd -c /tmp/$coredir/n9 -- $filedir/track_target.py -my 9 -u 1 2 3 4 6 7 8 9 -t 11 12 13 14 16 17 18 19 -i 500 -p $1 > /tmp/track_n1.log 2>&1 &


