import socket

from _thread import start_new_thread

import pickle


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind(('', 12345))
# binds the server to an entered IP address and at the specified port number.
# The client must be aware of these parameters
server.listen(100)
# listens for 100 active connections. This number can be increased as per convenience
list_of_clients=[]

def clientthread(conn, addr,name):
    conn.send(pickle.dumps("Welcome to this chatroom! Type exit to leave"))
    # sends a message to the client whose user object is conn
    while True:
            try:
                message = pickle.loads(conn.recv(2048))
                if message:
                    print("<" + name + "> " + message)
                    message_to_send = "<" + name + "> " + message
                    broadcast(message_to_send,conn)
                    # prints the message and address of the user who just sent the message on the server terminal
                else:
                    remove(conn)
            except:
                continue

def broadcast(message,connection):
    # sends out sent messages to every other connected client
    for clients in list_of_clients:
        if clients != connection:
            try:

                clients.send(pickle.dumps(message))
            except:
                clients.close()
                remove(clients)

def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)

while True:
    conn, addr = server.accept()
    list_of_clients.append(conn)
    message = pickle.loads(conn.recv(2048))
    print('{} connected'.format(message))
    print(addr[0] + " connected")
    # maintains a list of clients for ease of broadcasting a message to all available people in the chatroom
    # Prints the address of the person who just connected
    start_new_thread(clientthread,(conn,addr,message))
    # threading.Thread.(clientthread,(conn,addr))
    # creates and individual thread for every user that connects

conn.close()
server.close()