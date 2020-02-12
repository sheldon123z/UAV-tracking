#!/bin/bash



# Set directory variables
coredir=$(ls /tmp | grep pycore)
filedir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Terminate tcpdump processes
vcmd -c /tmp/$coredir/n1 -- killall tcpdump
vcmd -c /tmp/$coredir/n2 -- killall tcpdump
vcmd -c /tmp/$coredir/n3 -- killall tcpdump
vcmd -c /tmp/$coredir/n4 -- killall tcpdump
vcmd -c /tmp/$coredir/n6 -- killall tcpdump
vcmd -c /tmp/$coredir/n7 -- killall tcpdump
vcmd -c /tmp/$coredir/n8 -- killall tcpdump
vcmd -c /tmp/$coredir/n9 -- killall tcpdump

# Set node MAC addresses
export MAC_N1=`vcmd -c /tmp/$coredir/n1 -- cat /sys/class/net/eth0/address`
export MAC_N2=`vcmd -c /tmp/$coredir/n2 -- cat /sys/class/net/eth0/address`
export MAC_N3=`vcmd -c /tmp/$coredir/n3 -- cat /sys/class/net/eth0/address`
export MAC_N4=`vcmd -c /tmp/$coredir/n4 -- cat /sys/class/net/eth0/address`
export MAC_N6=`vcmd -c /tmp/$coredir/n6 -- cat /sys/class/net/eth0/address`
export MAC_N7=`vcmd -c /tmp/$coredir/n7 -- cat /sys/class/net/eth0/address`
export MAC_N8=`vcmd -c /tmp/$coredir/n8 -- cat /sys/class/net/eth0/address`
export MAC_N9=`vcmd -c /tmp/$coredir/n9 -- cat /sys/class/net/eth0/address`

# Start monitoring messages at each node using tcpdump
vcmd -c /tmp/$coredir/n1 -- tcpdump -i eth0 ether src $MAC_N1 and udp and dst 235.1.1.1 -lnex -x > /tmp/control_n1.dat 2>/dev/null 2>&1 &
vcmd -c /tmp/$coredir/n2 -- tcpdump -i eth0 ether src $MAC_N2 and udp and dst 235.1.1.1 -lnex -x > /tmp/control_n2.dat 2>/dev/null 2>&1 &
vcmd -c /tmp/$coredir/n3 -- tcpdump -i eth0 ether src $MAC_N3 and udp and dst 235.1.1.1 -lnex -x > /tmp/control_n3.dat 2>/dev/null 2>&1 &
vcmd -c /tmp/$coredir/n4 -- tcpdump -i eth0 ether src $MAC_N4 and udp and dst 235.1.1.1 -lnex -x > /tmp/control_n4.dat 2>/dev/null 2>&1 &
vcmd -c /tmp/$coredir/n6 -- tcpdump -i eth0 ether src $MAC_N6 and udp and dst 235.1.1.1 -lnex -x > /tmp/control_n6.dat 2>/dev/null 2>&1 &
vcmd -c /tmp/$coredir/n7 -- tcpdump -i eth0 ether src $MAC_N7 and udp and dst 235.1.1.1 -lnex -x > /tmp/control_n7.dat 2>/dev/null 2>&1 &
vcmd -c /tmp/$coredir/n8 -- tcpdump -i eth0 ether src $MAC_N8 and udp and dst 235.1.1.1 -lnex -x > /tmp/control_n8.dat 2>/dev/null 2>&1 &
vcmd -c /tmp/$coredir/n9 -- tcpdump -i eth0 ether src $MAC_N9 and udp and dst 235.1.1.1 -lnex -x > /tmp/control_n9.dat 2>/dev/null 2>&1 &


# Wait 10 seconds
#sleep 100s

# Begin testing simulation
python $filedir/test_uavs.py -u 1 2 3 4 6 7 8 9 -t 11 12 13 14 16 17 18 19 -l 6 2>/dev/null 2>&1 

# Wait 5 seconds
#sleep 5s

# Use trptr to obtain output files to plot
echo "Plotting graphs for uav nodes..."

trpr input /tmp/control_n1.dat auto X output /tmp/plot_n1.dat 2>/dev/null 2>&1 
trpr input /tmp/control_n2.dat auto X output /tmp/plot_n2.dat 2>/dev/null 2>&1 
trpr input /tmp/control_n3.dat auto X output /tmp/plot_n3.dat 2>/dev/null 2>&1 
trpr input /tmp/control_n4.dat auto X output /tmp/plot_n4.dat 2>/dev/null 2>&1 
trpr input /tmp/control_n6.dat auto X output /tmp/plot_n6.dat 2>/dev/null 2>&1 
trpr input /tmp/control_n7.dat auto X output /tmp/plot_n7.dat 2>/dev/null 2>&1 
trpr input /tmp/control_n8.dat auto X output /tmp/plot_n8.dat 2>/dev/null 2>&1 
trpr input /tmp/control_n9.dat auto X output /tmp/plot_n9.dat 2>/dev/null 2>&1 

# Uncomment if plots of each individual node are needed
#gnuplot -persist /tmp/plot_n1.dat 2>/dev/null 2>&1 &
#gnuplot -persist /tmp/plot_n2.dat 2>/dev/null 2>&1 &
#gnuplot -persist /tmp/plot_n3.dat 2>/dev/null 2>&1 &
#gnuplot -persist /tmp/plot_n4.dat 2>/dev/null 2>&1 &
#gnuplot -persist /tmp/plot_n6.dat 2>/dev/null 2>&1 &
#gnuplot -persist /tmp/plot_n7.dat 2>/dev/null 2>&1 &
#gnuplot -persist /tmp/plot_n8.dat 2>/dev/null 2>&1 &
#gnuplot -persist /tmp/plot_n9.dat 2>/dev/null 2>&1 &

# Plot all UAV node throughput on one graph
gnuplot plot_uavs.gp 
eog uavs_throughput_plot.png &

# Disown script to exit out in terminal
disown 
