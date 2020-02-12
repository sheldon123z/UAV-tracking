--------------------------------------------------------------------
Background Info
--------------------------------------------------------------------

Demo for showing coordination between a number of UAVs regarding tracking an equal number of targets.
In the ideal case, each UAV tracks one target, different than the one tracked by any other UAV.

Sample Mission Scenario:
	- Each UAV can track only one target at a time
	- Once tracking a target, a UAV “locks” on it
	- Does not switch targets unless the current one gets out of range

(Very) Simple Algorithm:
	- Find a target
	- If the target is already tracked, then search for another one
	- If the target is not tracked, then advertise to others that the target is now tracked
	- Start tracking the target
	
--------------------------------------------------------------------
Creating the emulation testbed
--------------------------------------------------------------------

Download and install CORE emulation environment:
	 - Follow instructions at https://github.com/coreemu/core 

Allow CORE daemon to listen on the control interface:
         - edit /etc/core/core.conf
      	 - change "listenaddr = localhost" to "listenaddr = 0.0.0.0"

Running CORE

  	1. start core daemon
	
		sudo service core-daemon start

  	2. start core GUI

		core-gui

  	3. create or load scenario

--------------------------------------------------------------------
Running the software
--------------------------------------------------------------------

Create a symlink /data/uas-core/ to the folder where you download the software

To run it, start the .imn file in CORE and then on a terminal on the host machine run ./start_tracking.sh <service> where <service> is:
	- none (means no comms at all)
	- udp

UAVs should start moving after running the ./start_tracking.sh command first time. If they don't something's not right.

Drag targets to the left towards the UAVs and then they'll start tracking the targets. Drag targets way to the right of the screen and they'll lose them.

After stopping CORE, remove text files in the /tmp folder that keep node positions and colors. Otherwise next time you run it nodes will be placed/colored as they were just before stopping CORE

sudo rm /tmp/*.txt


*** Note that there are hard-coded absolute paths in the .imn file and the .py and .sh scripts. Likely they won't work out of the box and need to be changed.

*** By default CORE will not allow moving nodes during automated mobility. To allow moving the target nodes comment out the following line in proc moveNode {} in /usr/local/lib/core/wlan.tcl

$c dtag node selected

*** By default CORE will show links between UAVs. The demo looks better with the wireless links disabled. To turn them off comment the following line in /usr/local/lib/core/api.tcl (last line in "proc apiLinkAddModify {}") and restart CORE:

drawWlanLink $node1 $node2 $wlan


--------------------------------------------------------------------
Testing
--------------------------------------------------------------------

	
	1. Run uav test script scenario to measure latency and throughput. 

		./start_testing.sh

	Note: 	[1] The test script 'start_testing.sh' tracks the latency and throughput of the testing protocol. 
			Within the test script, 'test_uavs.py' is called, which moves all nodes within range and waits until all uav nodes track a 				target.
			[2] Once the test script is finished, search for the following files: 
				gedit /tmp/norm_latency_avg.log
				eog $(file_dir)/uavs_throughput_plot.png 
				[a] $(file_dir) needs to be replaced with the directory of the file.

	2. (Optional) Run uav python file to measure latency.

	Example:[1]	python $(file_dir)/test_uavs.py -u 1 2 3 4 6 7 8 9 -t 11 12 13 14 16 17 18 19 -l 6		# 6 Runs
			[2] python $(file_dir)/test_uavs.py -u 1 2 3 4 6 7 8 9 -t 11 12 13 14 16 17 18 19 -l 2		# 2 Runs

	Note: 	[1] $(file_dir) needs to be replaced with the directory of the file.
			[2] Once the test script is finished, search for the following file to view latency log file: 
				gedit /tmp/norm_latency_avg.log
		
		









