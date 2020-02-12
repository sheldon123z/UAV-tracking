set terminal png size 1500,600
set output 'uavs_throughput_plot.png'

set xdata time
set timefmt "%s" # can use set format "%.1s"
set format x "%.1s"
set xlabel "Time (sec)"

set autoscale

set ylabel "Rate (kbps)"
set format y "%.1s"

set title "Throughput of UAV nodes"
set key reverse Left outside
set grid

set style data linespoints

#set terminal svg size 800, 800
set xtics 0,5
set ytics 0,10
plot "/tmp/plot_n1.dat" using 1:2 w l title "Node 1", \
	"/tmp/plot_n2.dat" using 1:2 w l title "Node 2", \
	"/tmp/plot_n3.dat" using 1:2 w l title "Node 3", \
	"/tmp/plot_n4.dat" using 1:2 w l title "Node 4", \
	"/tmp/plot_n6.dat" using 1:2 w l title "Node 6", \
	"/tmp/plot_n7.dat" using 1:2 w l title "Node 7", \
	"/tmp/plot_n8.dat" using 1:2 w l title "Node 8", \
	"/tmp/plot_n9.dat" using 1:2 w l title "Node 9", \

set xtics auto
set ytics auto

