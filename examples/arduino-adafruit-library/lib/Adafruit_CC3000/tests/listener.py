# Adafruit CC3000 Library Test Listener
# Created by Tony DiCola (tony@tonydicola.com)
# Released with the same license as the Adafruit CC3000 library (BSD)

# Create a simple server to listen by default on port 9000 (or on the port specified in
# the first command line parameter), accept any connections and print all data received
# to standard output.  Must be terminated by hitting ctrl-c to kill the process!

from socket import *
import sys
import threading

SERVER_PORT = 9000
if len(sys.argv) > 1:
	SERVER_PORT = sys.argv[1]

# Create listening socket
server = socket(AF_INET, SOCK_STREAM)

# Ignore waiting for the socket to close if it's already open.  See the python socket
# doc for more info (very bottom of http://docs.python.org/2/library/socket.html).
server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

# Listen on any network interface for the specified port
server.bind(('', SERVER_PORT))
server.listen(5)

# Worker process to print all data received to standard output.
def process_connection(client):
	while True:
		data = client.recv(1024)
		sys.stdout.write(data) # Don't use print because it appends spaces and newlines
		sys.stdout.flush()
		if not data: 
			break
	client.close()

try:
	# Wait for connections and spawn worker threads to process them.
	while True:
		client, address = server.accept()
		thread = threading.Thread(target=process_connection, args=(client,))
		thread.start()
except:
	server.close()