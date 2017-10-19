import socket, select
import os


class Server(object):
    # List to keep track of socket descriptors
    CONNECTION_LIST = []
    RECV_BUFFER = 4096  # Advisable to keep it as an exponent of 2
    
    def __init__(self):       
        self.server="localhost"
        self.port = 5003
        self.user_name_dict = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.JOINED_MSG = 'JOINED_CHATROOM: {}\nSERVER_IP: {}\nPORT: {}\ROOM_REF: {}\nJOIN_ID: {}'
        self.LEFT_MSG = 'LEFT_CHATROOM: {}\nJOIN_ID: {}'

        self.chatrooms = {}
        self.CurrentChatroomID = 1

        self.clients = {}
        self.CurrentClientID = 100


        self.set_up_connections()
        self.client_connect()

    def set_up_connections(self):
        # this has no effect, why ?
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.server, self.port))
        self.server_socket.listen(10)  # max simultaneous connections.

        # Add server socket to the list of readable connections
        self.CONNECTION_LIST.append(self.server_socket)

    # Function to broadcast chat messages to all connected clients
    def broadcast_data(self, sock, message):
        # Do not send the message to master socket and the client who has send us the message
        for socket in self.CONNECTION_LIST:
            if socket != self.server_socket and socket != sock:
                # if not send_to_self and sock == socket: return
                try:
                    socket.send(message)
                except:
                    # broken socket connection may be, chat client pressed ctrl+c for example
                    socket.close()
                    self.CONNECTION_LIST.remove(socket)

    def send_data_to(self, sock, message):
        try:
            sock.send(message)
        except:
            # broken socket connection may be, chat client pressed ctrl+c for example
            socket.close()
            self.CONNECTION_LIST.remove(sock)

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
            if str(val) == str(roomid):
                roomname = key
        print (roomname)
        return roomname
    
#    chatrooms[2] ='b'
#    for key, val in chatrooms.items():
#        print (key, val)
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
    def join_chat(self, data):
        cr = self.getRight(data[0])
        if cr not in self.chatrooms:
            self.chatrooms[cr] = self.CurrentChatroomID 
            self.CurrentChatroomID +=1
        
        assert(self.getLeft(data[1]) == 'CLIENT_IP')
        assert(self.getLeft(data[2]) == 'PORT')
        assert(self.getLeft(data[3]) == 'CLIENT_NAME')
        
        cn = self.getRight(data[3])
        if cn not in self.clients:
            self.clients[cn] = self.CurrentClientID
            self.CurrentClientID +=1
        return self.JOINED_MSG.format(cr, self.server, self.port, self.chatrooms[cr], self.clients[cn])

    #RECEIVED MESSAGE:
    #LEAVE_CHATROOM: [ROOM_REF]
    #JOIN_ID: [integer previously provided by server on join]
    #CLIENT_NAME: [string Handle to identifier client user]
    
    #RETURNS:
    #LEFT_CHATROOM: [ROOM_REF]
    #JOIN_ID: [integer previously provided by server on join]
    def leave_chat(self, data):
        cr = int(self.getRight(data[0]))
        roomname = self.findRoomNameByID(cr)

        if roomname == 'not found':
            return 'ERROR_CODE: 200\nERROR_DESCRIPTION: You are requesting to leave a chatroom that doesnt exist'
        
        assert(self.getLeft(data[1]) == 'JOIN_ID')
        assert(self.getLeft(data[2]) == 'CLIENT_NAME')
        
        join_id = int(self.getRight(data[1]))
        client_name = self.getRight(data[2])
        
        if self.clients[client_name] != join_id:
            return 'ERROR_CODE: 210\nERROR_DESCRIPTION: Client name and join ID do not match'
        
        #do the actual leave??
        
        return self.LEFT_MSG.format(cr, join_id)
      
        
    #data = 'JOIN_CHATROOM: chat1\nCLIENT_IP: 123.456.789.000\nPORT: 123\nCLIENT_NAME: client1'     
    #data = data.splitlines()   
    #getLeft(data[0])   
    #getRight(data[0])   
    def client_connect(self):
        print ("Chat server started on port " + str(self.port))
        while 1:
            # Get the list sockets which are ready to be read through select
            read_sockets, write_sockets, error_sockets = select.select(self.CONNECTION_LIST, [], [])

            for sock in read_sockets:
                if sock == self.server_socket: #New connection
                    self.setup_connection()
                else:
#                    try:
                    data = sock.recv(self.RECV_BUFFER)
                    data = data.decode('utf-8')
                    if data:
                        if data =='EXIT':
                            os._exit(1)
                            
                        data = data.splitlines() #Ex: ['JOIN_CHATROOM: {}', 'CLIENT_IP: {}', 'PORT: {}', 'CLIENT_NAME: {}']
                        
                        #First item of the message should be the action:
                        action = self.getLeft(data[0])
                        if action == 'JOIN_CHATROOM':
                            print('Join Chatroom request')
                            result = self.join_chat(data)
                            self.send_data_to(sock, result.encode('utf-8'))
                        elif action == 'LEAVE_CHATROOM':
                            print('Leave Chatroom request')
                            result = self.leave_chat(data)
                            self.send_data_to(sock, result.encode('utf-8'))
#                            if self.user_name_dict[sock].username is None:
#                                self.set_client_user_name(data, sock)
#                            else:
#                                self.broadcast_data(sock, "\r" + '<' + self.user_name_dict[sock].username + '> ' + data)

#                    except Exception as ex:
#                        print (ex)
#                        sock.close()
#                        self.CONNECTION_LIST.remove(sock)
#                        continue

        self.server_socket.close()

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
    server = Server()