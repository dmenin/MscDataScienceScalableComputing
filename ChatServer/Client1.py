# -*- coding: utf-8 -*-
import socket
import sys

#socket.gethostname()

def create_client_socket():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Connect the socket to the port where the server is listening
    server_address = ('localhost', 5000)#10.6.43.95 #'localhost' 
    print ('Connecting to %s port %s' % server_address)
    sock.connect(server_address)
    return sock


def send_msg(msg):
    sock = create_client_socket()
    try:        
        sock.sendall(msg.encode('utf-8'))
    
        data = sock.recv(4096)
        print ('Received "%s"' % data)
    finally:
        sock.close()


JOIN_MSG='JOIN_CHATROOM: {}\nCLIENT_IP: {}\nPORT: {}\nCLIENT_NAME: {}\n'
LEAVE_MSG='LEAVE_CHATROOM: {}\nJOIN_ID: {}\nCLIENT_NAME: {}'
CHAT_MSG='CHAT: {}\nJOIN_ID: {}\nCLIENT_NAME: {}\nMESSAGE: {}'#needs to end with \n\n

#send_msg(msg)
##
##
#send_msg(JOIN_MSG.format('chat1','123.456.789.000','123','client1'))
##
#send_msg(LEAVE_MSG.format('1', '101', 'client1'))
##send_msg('KILL_SERVICE')
#

#1)Client 1 joins chat1
#sock1 = create_client_socket()
#msg = JOIN_MSG.format('chat1','123.456.789.000','123','client1')
#sock1.sendall(msg.encode('utf-8'))
#print ('Received "%s"' % sock1.recv(4096))
#
#
#CHAT_MSG='CHAT: {}\nJOIN_ID: {}\nCLIENT_NAME: {}\nMESSAGE: {}'.format('1', '100', 'client1', 'HIIIIIIII')
#sock1.sendall(CHAT_MSG.encode('utf-8'))
#
#
#
#sock2.sendall(LEAVE_MSG.format('1', '100', 'client1').encode('utf-8'))
#print ('Received "%s"' % sock2.recv(4096))
#
#
#
#
#
#sock2 = create_client_socket()
#msg = JOIN_MSG.format('chat1','123.456.789.000','123','client2')
##msg = 'HELO text\n'
#msg = 'CHATROOMS'       
#sock2.sendall(msg.encode('utf-8'))
#print ('Received "%s"' % sock2.recv(4096))
#
#
#
#msg = LEAVE_MSG.format('1', '100', 'client1')
#sock.sendall(msg.encode('utf-8'))
#print ('Received "%s"' % sock.recv(4096))
#
#
#sock.close()
# 

import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 5000) #'localhost' 
sock.connect(server_address)

#msg = 'HELO its me\n'
#msg='KILL_SERVICE'
JOIN_MSG='JOIN_CHATROOM: {}\r\nCLIENT_IP: {}\r\nPORT: {}\r\nCLIENT_NAME: {}\r\n'
msg = JOIN_MSG.format('chat1','123.456.789.000','123','client2')
print (msg)

#msg='JOIN_CHATROOM: oloco\n'
sock.send(msg.encode('utf-8'))

#print ('Received "%s"' % sock.recv(4096))
#sock.close()


 
 
 
 
 
 
 