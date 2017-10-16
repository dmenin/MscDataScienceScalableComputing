import socket
import os

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


server_address = ('localhost', 10004)
print ('starting up on %s port %s' % server_address)

sock.bind(server_address)
sock.listen(1)

try:
    while True:
        # Wait for a connection
        print ('waiting for a connection')
        connection, client_address = sock.accept()
        
        try:
            print ('   Connection from', client_address)
    
            # Receive the data in small chunks and retransmit it
            while True:
                data = connection.recv(16)
                print ('   Received "%s"' % data)
                if data:
                    print ('   Sending data back to the client')
                    connection.sendall(data)
                else:
                    print ('   No more data from', client_address)
                    break
        finally:
            print('Clean up the connection')
            connection.close()
finally:
    print('Shutting down')
    sock.shutdown(1)
    sock.close()
    os._exit(1)