import socket, select
import os
import argparse

class ChatRoom:

    def __init__(self, name, ID):
        self.name = name
        self.ID = ID

        #list of tuples
        self.clients = []
    
    def ShowMe(self):
        '''
        Print info about the ChatRoom and its members
        '''
        print('#Chatroom ID:{}, Name:{} -- Clients:'.format(self.ID, self.name))
        for c in self.clients:
            print('#    Client ID: {} Name:{}'.format(c[1], c[0]))
            
    def AddClient(self, name, id, socket):
        self.clients.append((name, id, socket))

    def RemoveClient(self, name, id):
        #print (self.name, self.ID, name, id)
        self.clients = [l for l in self.clients if l[0] != name]
    
    def SendToAllInTheRoom(self, msg, clientname=''):
        msg = "CHAT: {0}\nCLIENT_NAME: {1}\nMESSAGE: {2}\n\n".format(self.ID, clientname, msg)
        print('Brodcasting msg on room {}: {}'.format(self.name, msg))

        for c in self.clients:
            print('Sending to client {}'.format(c[0]))
            s = c[2]
            s.send(msg.encode('utf-8'))

class Server(object):
    # List to keep track of socket descriptors
    CONNECTION_LIST = []
    RECV_BUFFER = 4096  # Advisable to keep it as an exponent of 2
    
    def __init__(self, host = None, port = 5000):
        

        if host == None: 
            #no parameter specified, either my local dev or deployed @ nebula
            if socket.gethostname() == 'DESKTOP-MH1VBMC':
                self.server = 'localhost'
            else:
                self.server='10.62.0.17' #Nebula Instance
            #self.server = '10.6.43.95' #TCD - not working on TCDWifi
        else:
            self.server = host
        self.port = port
        
        print (self.server, self.port)
        

        self.user_name_dict = {}
        self.myStudentId = 13312410
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.HELLO_MSG  = 'HELO {}\nIP:{}\nPort:{}\nStudentID:{}'
        self.JOINED_MSG = 'JOINED_CHATROOM: {}\nSERVER_IP: {}\nPORT: {}\nROOM_REF: {}\nJOIN_ID: {}\n'
        self.LEFT_MSG   = 'LEFT_CHATROOM: {}\nJOIN_ID: {}\n'
        

        self.chatrooms = {}
        self.CurrentChatroomID = 1

        self.clients = {}
        self.CurrentClientID = 100

        self.set_up_connections()
        self.client_connect()

    def set_up_connections(self):
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.server, self.port))
        self.server_socket.listen(10)  # max simultaneous connections.

        # Add server socket to the list of readable connections
        self.CONNECTION_LIST.append(self.server_socket)

    def send_data_to(self, sock, message):
        print('Sending:', message)
        sock.send(message)

    def getLeft(self, data):
        '''
        Get the left part of a line:
        'JOIN_CHATROOM: {123}' returns JOIN_CHATROOM
        '''
        return data[0:data.find(' ')-1]

    def getRight(self, data):
        '''
        Get the right part of a line:
        'JOIN_CHATROOM: {123}' returns 123
        '''
        return data[data.find(' ')+1: len(data)]

    def findRoomNameByID(self, roomid):
        roomname='not found'
        
        for key, val in self.chatrooms.items():
            #val is the ChatRoom Object
            if str(val.ID) == str(roomid):
                roomname = key
        return roomname


    #RECEIVED MESSAGE:
    #JOIN_CHATROOM: [chatroom name]
    #CLIENT_IP: [IP Address of client if UDP | 0 if TCP]
    #PORT: [port number of client if UDP | 0 if TCP]
    #CLIENT_NAME: [string Handle to identifier client user]
    
    #RETURNS:
    #JOINED_CHATROOM: [chatroom name]
    #SERVER_IP: [IP address of chat room]
    #PORT: [port number of chat room]
    #ROOM_REF: [integer that uniquely identifies chat room on server]
    #JOIN_ID: [integer that uniquely identifies client joining]
    def join_chat(self, data, socket):
        assert(self.getLeft(data[1]) == 'CLIENT_IP')
        assert(self.getLeft(data[2]) == 'PORT')
        assert(self.getLeft(data[3]) == 'CLIENT_NAME')

        cn  = self.getRight(data[3])        
        if cn not in self.clients:
            #Create new client if it doesnt exist
            self.clients[cn] = self.CurrentClientID
            self.CurrentClientID +=1
        
        #Check if client is already on the chatroom??
        
        chatname = self.getRight(data[0])
        if chatname not in self.chatrooms:
            #Creating a New ChatRoom
            c = ChatRoom(chatname, self.CurrentChatroomID) 
            self.chatrooms[chatname] = c 
            self.CurrentChatroomID +=1
        else:
            c = self.chatrooms[chatname]
        
        
        c.AddClient(cn, self.clients[cn], socket)
        result = self.JOINED_MSG.format(chatname, self.server, self.port, 
                                      self.chatrooms[chatname].ID, self.clients[cn])

        self.send_data_to(socket, result.encode('utf-8'))
        c.SendToAllInTheRoom('{} has joined this chatroom.'.format(cn), cn)


    #RECEIVED MESSAGE:
    #LEAVE_CHATROOM: [ROOM_REF]
    #JOIN_ID: [integer previously provided by server on join]
    #CLIENT_NAME: [string Handle to identifier client user]
    
    #RETURNS:
    #LEFT_CHATROOM: [ROOM_REF]
    #JOIN_ID: [integer previously provided by server on join]
    def leave_chat(self, data, socket):
        chatroomid = int(self.getRight(data[0]))        
        roomname = self.findRoomNameByID(chatroomid)

        if roomname == 'not found':
            return 'ERROR_CODE: 200\nERROR_DESCRIPTION: You are requesting to leave a chatroom that doesnt exist'
        
        assert(self.getLeft(data[1]) == 'JOIN_ID')
        assert(self.getLeft(data[2]) == 'CLIENT_NAME')
        join_id = int(self.getRight(data[1]))
        client_name = self.getRight(data[2])
        
        if self.clients[client_name] != join_id:
            return 'ERROR_CODE: 210\nERROR_DESCRIPTION: Client name and join ID do not match'
        
        c = self.chatrooms[roomname]
        #self.chatrooms[roomname].RemoveClient(client_name, join_id)
        
        result =  self.LEFT_MSG.format(chatroomid, join_id)
        self.send_data_to(socket, result.encode('utf-8'))
        c.SendToAllInTheRoom('{}  has left this chatroom.'.format(client_name), client_name)
        c.RemoveClient(client_name, join_id)

        
    #Receive:
    #CHAT: [ROOM_REF]
    #JOIN_ID: [integer identifying client to server]
    #CLIENT_NAME: [string identifying client user]
    #MESSAGE: [string terminated with '\n\n']
    
    #BroadCasts:
    #CHAT: [ROOM_REF]
    #CLIENT_NAME: [string identifying client user]
    #MESSAGE: [string terminated with '\n\n']
    def send_message(self, data):
        print (data)
        assert(self.getLeft(data[1]) == 'JOIN_ID')
        assert(self.getLeft(data[2]) == 'CLIENT_NAME')
        assert(self.getLeft(data[3]) == 'MESSAGE')
        
        chatroomid  = int(self.getRight(data[0])) 
        roomname = self.findRoomNameByID(chatroomid)
        c = self.chatrooms[roomname]
        client_name = self.getRight(data[2])
        msg         = self.getRight(data[3])        

        c.SendToAllInTheRoom(msg, client_name)

    #DISCONNECT: [IP address of client if UDP | 0 if TCP]
    #PORT: [port number of client it UDP | 0 id TCP]
    #CLIENT_NAME: [string handle to identify client user]
    def disconnect(self, data, socket):
        assert(self.getLeft(data[1]) == 'PORT')
        assert(self.getLeft(data[2]) == 'CLIENT_NAME')
        cn = self.getRight(data[2])
        
        #loop troguh the rooms
        for roomID, room in sorted(self.chatrooms.items()):
            print('Room:{}'.format(room.name))
            #clients connected to the room; (name, id, socket)
            for c in room.clients:
                if c[0] == cn and socket == c[2]:
                    print('    Client is in the room'.format(cn))
                    room.SendToAllInTheRoom('{}  has left this chatroom.'.format(cn), cn)
                    room.RemoveClient(cn, 0)
                    break

    def client_connect(self):
        print ("Chat server started on {}:{}".format(str(self.server),str(self.port)))
        while 1:
            # Get the list sockets which are ready to be read through select
            read_sockets, write_sockets, error_sockets = select.select(self.CONNECTION_LIST, [], [])
            try:
                print('len: {}'.format(len(read_sockets)))
                for sock in read_sockets:
                    if sock == self.server_socket: #New connection
                        print ('New Connection')
                        self.setup_connection()
                    else:
                        #try:
                        data = sock.recv(self.RECV_BUFFER)
                        data = data.decode('utf-8')
                        if data:
                            if data == 'KILL_SERVICE\n':
                                print('Killing Chat Service')
                                os._exit(1)
                            if data == 'CHATROOMS': #DEBUG
                                self.ShowChatRooms()
        
                            data = data.splitlines()
                            #First item of the message should be the action:
                            action = self.getLeft(data[0])
                            #print ('Action:', action)
                            
                            if action == 'HEL': #all actions have a ":", except the "hello" action
                                print('Helo Sent')
                                returnmsg = self.getRight(data[0])
                                self.send_data_to(sock, self.HELLO_MSG.format(returnmsg, self.server, self.port, self.myStudentId).encode('utf-8'))
                            elif action == 'JOIN_CHATROOM':
                                print('Join Chatroom request')
                                self.join_chat(data, sock)
                            elif action == 'LEAVE_CHATROOM':
                                print('Leave Chatroom request')
                                self.leave_chat(data, sock)
                            elif action == 'CHAT':
                                print('Chat Message')
                                self.send_message(data)   
                            elif action == 'DISCONNECT':
                                print('Disconect')
                                self.disconnect(data, sock)
                                print('Close Sock')
                                sock.close()
                                print('Remove Sock')
                                self.CONNECTION_LIST.remove(sock)
            except Exception as ex:
                print (ex)
                sock.close()
                self.CONNECTION_LIST.remove(sock)
                continue

        self.server_socket.close()
    
    def ShowChatRooms(self):
        print('\n############## Listing all {} chatrooms:############### '.format(len(self.chatrooms)))
        for c in self.chatrooms:
            self.chatrooms[c].ShowMe()
        print('#######################################################')

    def set_client_user_name(self, data, sock):
        self.user_name_dict[sock].username = data.strip()
        self.send_data_to(sock, data.strip() + ', you are now in the chat room\n')
        self.send_data_to_all_regesterd_clents(sock, data.strip() + ', has joined the cat room\n')

    def setup_connection(self):
        sockfd, addr = self.server_socket.accept()
        self.CONNECTION_LIST.append(sockfd)
        print ("Client (%s, %s) connected" % addr)
        #self.send_data_to(sockfd, "please enter a username: ")
        self.user_name_dict.update({sockfd: Connection(addr)})

    def send_data_to_all_regesterd_clents(self, sock, message):
        for local_soc, connection in self.user_name_dict.iteritems():
            if local_soc != sock and connection.username is not None:
                self.send_data_to(local_soc, message)


class Connection(object):
    def __init__(self, address):
        self.address = address
        self.username = None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host',type=str,  default=None, help='Server''s IP.')
    parser.add_argument('--port', type=int, default=5000, help='Server''s port .')
    args, extra  = parser.parse_known_args()
    
    server = Server(args.host, args.port)
