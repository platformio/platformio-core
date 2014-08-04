Adafruit CC3000 Library Tests
=============================

This folder is meant to contain tests that are written to verify the CC3000 library.  Consumers
of the library probably want to ignore the contents of this folder.

Files:
------

-	listener.py
	
	Python script to run a TCP socket server which listens by default on port 9000 (but can be
	changed by specifying a different port in the first command line parameter), accepts any
	connections and echos all received data to standard output.  This is required for running some
	of the tests.  In general you'll want to run listener.py with stdout directed to a file and then
	run the test sketch on the CC3000 to capture what is output.  Compare the output of test runs
	before and after making a change/bugfix to the library and diff the results to ensure no
	unexpected changes in functionality.

Tests:
------

-	Client\_fastrprint

	Manual test to verify the fastrprint and fastrprintln functions of the client library.  Must
	update the sketch to connect to your wireless network and set the SERVER_IP value to the IP
	of a server running listener.py.