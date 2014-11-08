#!/etc/python
#Sean DeBellis copyright 2014 
#This is an IRC Server
#
from socket import *
from select import *
from threading import *
#command definitions:
#   /nick - alias a name
#   /list - lists all of the channels
#   /msg - private message 
#   /whois - returns proper name, what channels they're in, what server they logged into 
#   /join - join a room 
#   /leave - leave a room
'''
class clientObj:
    _IP = None
    _nick = ''
    _sock = None
    _rooms = []

    def __init__(self, ip, sock):
        self._IP = ip
        self._sock = sock
    
    def add_to_room(self, roomName):
        self._rooms.append(roomName)

    def get_ip(self):
        return self._IP

    def get_rooms(self):
        return self._rooms

    def get_socket(self):
        return self._sock

    def remove_from_room(self, roomName):
        if roomName is in self._rooms:
            self._rooms.remove(roomName)

    def set_nickname(self, nick):
        self._nick = nick
'''
class ircServer:
    
    _HOST = ''
    _PORT = None
    _masterSocket = None
    _clientsNick = dict() #hashes ip's to client nick
    _clientSockets = dict() #hashes ips to sockets
    _rooms = dict() # hashes room names to list of ips in room
    _lobby = [] # list for clients that are not in a room. Any message
                # input will return an error message until they join a room.
    _incomingSockets = []
    _outgoingSockets = []
    _errorSockets = []
   
    def __init__(self, serverPort=5000):
        self._PORT = serverPort
        self._masterSocket = socket(AF_INET, SOCK_STREAM)
        self._masterSocket.bind((self._HOST , self._PORT ))
        self._masterSocket.listen(5)
        self._incomingSockets.append(self._masterSocket)

    def close(self):
        print 'server closing connection'
        self._masterSocket.shutdown(SHUT_RDWR)
	self._masterSocket.close()

    #def add_client_to_room(clientName, roomName):
        
    #Searches the clientsNick data member for the clients
    #nickname for the given ip key. Returns none if not in the map.
    def get_client_nick(self,ip):
        return self._clientsNick.get(ip)

    #Searches the _rooms map to get a list of all the ips in a room
    # determined by the roomName argument. Returns none if room does not exist.
    def get_clients_in_room(self,roomName):
        return self._rooms.get(roomName)
    
    #Returns a socket object that belongs to the ip address passed into the function.
    # Returns None if key doesn't exist
    def get_client_socket(self,ip):
        return self._clientSockets.get(ip)
    
    #Checks the master socket for waiting connections and if they are present
    #   adds them to the list of client sockets
    #   it also calls a receive which must carry the hostname of the computer
    #   being logged on by.
    def get_new_connections(self, ready_to_connect):
        to_read, to_write, err = select(self._incomingSockets, self._outgoingSockets, self._errorSockets, 10)
        
        for sock in to_read:
                print sock
                if sock == self._masterSocket:
                    conn, addr = sock.accept()
                    self._clientSockets[addr] = conn
                    hostName = conn.recv(1024)
                    self._clientsNick[addr[0]] = hostName
                    #self.lobby.append(conn)
        print 'exiting get_new_connections'
        '''
        for sock in ready_to_connect:
            print sock
            if sock == self._masterSocket:
                conn, adddr = sock.accept()
                self._clientSockets[addr[0]] = conn
                host_name = conn.recv(1024)
                self._clientNick[addr[0]] = host_name
                self._lobby.append(conn)
        print 'exiting get_new_connection'
        '''
    


    #def get_incoming_messages():
    #def parse_message():
    #def broadcast_message():
    #def join_room(self, room_name):
    #def leave_room():
    
    def connection_dump(self):
        key_list = self._clientSockets.keys()
        if key_list is None:
            print 'empty socket list'
            return None
        else:
            return key_list

    def nickname_dump(self):
        key_list = self._clientsNick.keys()
        if key_list is None:
            print 'empty nickname list'
            return None
        else:
            for i in key_list:
                print self._clientsNick[i]

    def testGetNewConnections(self):
        #self.start_keyboard_thread()
        connected_ips = []
        old_list = []
        print 'in testGetNewConnection before loop'
        for i in range(0,10):
            print 'in testGetNewConnetion in loop'
            self.get_new_connections()
            print 'dumping connected sockets *****'
            connected_ips = self.connection_dump()
            if cmp(old_list, connected_ips) is 0:
                print 'no new connections'
            else:
                print connected_ips
                old_list = connected_ips
            print ''
            print ''
            print 'dumping nicknames *****'
            self.nickname_dump()




    #def run():
    #    while True:
    #        get_new_connections()





if __name__ == '__main__':
    server = None
    try:
        server = ircServer(5000)
        #try:
        server.testGetNewConnections()
        #except:
        print 'testGetNewConnections error: closing server'
        server.close()
    except:
        print 'server cannot be started'
           



'''
HOST = ''
PORT = 5000

server = socket(AF_INET, SOCK_STREAM)
server.bind((HOST,PORT))
server.listen(1)
conn, addr = server.accept()
print 'Connected by', addr
while 1:
    data = conn.recv(1024)
    if not data: break
    conn.sendall(data)
server.close()
'''