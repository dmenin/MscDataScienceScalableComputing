# -*- coding: utf-8 -*-
import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 5001)
print ('Connecting to %s port %s' % server_address)
sock.connect(server_address)


JOIN_MSG='JOIN_CHATROOM: {}\nCLIENT_IP: {}\nPORT: {}\nCLIENT_NAME: {}'
		

try:
    # Send data
    message = JOIN_MSG.format('chat1','123.456.789.000','123','client1')
    #print ('Sending "%s"' % message)
    sock.sendall(message.encode('utf-8'))
    #sock.send(message)
   
    # Look for the response
    amount_received = 0
    amount_expected = len(message)

    data = sock.recv(4096)
    print ('Received "%s"' % data)
        
#    while amount_received < amount_expected:
#        data = sock.recv(16)
#        amount_received += len(data)
#        print ('Received "%s"' % data)

finally:
    print ('Closing socket')
    sock.close()
    
