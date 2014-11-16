#!/etc/python
#Sean DeBellis copyright 2014 
#This is an IRC Server
#
from socket import *
from select import *
from threading import *
import re
#command definitions:
#   /nick - alias a name
#   /list - lists all of the channels
#   /msg - private message 
#   /whois - returns proper name, what channels they're in, what server they logged into 
#   /join - join a room 
#   /leave - leave a room

# Message format -
#   current room, [command, [args]* ], text



#*****************important read me ******************************
# Last worked:
# I am experiencing buffering problems where on the client side
#   its either stacking up in the buffer thats reading or
#   the socket is repeating the messages.
#First thing to do is run the program and keep tracking the
#   error.
#
#Needs:
#  need to figure out a better way to prepare strings for
#   transmission. They must be delimited with \r\n but im
#   doing it in many places and its getting confusing. If I have
#   one function that does it before every send then I can have
#   the string as normal and then add the delimiter just before
#   transmission.
#
#
#
#*****************IMPORTANT**************************************
# All messages shall be sent as comma seperated values and the
# message will be delimited with '\r\n'
#****************************************************************
class ircServer:
    
    _HOST = ''
    _PORT = None
    _masterSocket = None
    _clientsNick = dict() #hashes ip's to client nick
    _clientSockets = dict() #hashes ips to sockets
    _listeningSockets = [] #all of the sockets to be checked for incoming messages
    _rooms = dict() # hashes room names to list of ips in room
    _lobby = [] # list of client ip's that are not in a room. Any message
                # input will return an error message until they join a room.
    _incomingSockets = []
    _outgoingSockets = []
    _errorSockets = []


    #ERROR MESSAGES FOR return_err
    NO_ROOM_ERR = '101_room_error must be in a room to send messages'
    COMMAND_ERR = '201_command_error : is not a valid command'
    INCOMING_MSG_CMD = '100_incoming_message'
    JOIN_ACK = '300_room_joined'
    JOIN_MSG = 'has joined the room'

    def __init__(self, serverPort=5000):
        print 'in __init__'
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
    def get_new_connections(self):
        print 'in get_new_connections'
        to_read, to_write, err = select(self._incomingSockets, self._outgoingSockets, self._errorSockets, 10)
           
        for sock in to_read:
            if sock == self._masterSocket:
                conn, addr = sock.accept()
                self._clientSockets[addr[0]] = conn
                hostName = conn.recv(1024)
                self._clientsNick[addr[0]] = hostName
                self._listeningSockets.append(conn)
                self._lobby.append(addr[0])
        print 'exiting get_new_connections'
    
    def remove_from_all_rooms(self, ip):
        room_lists = self._rooms.values()
        for room in room_lists:
            room.remove(ip)
    
    def remove_client(self, ip):
        self.remove_from_all_rooms(ip)
        del self._clientNick[ip]
        

    def get_incoming_messages(self):
        print 'in get_incoming_messages'
        to_read, to_write, err = select(self._listeningSockets, [], self._listeningSockets, 10)

        #if there is any sockets in err
            #-get the sockets ip address
            #-remove ip from all rooms
            #-remove socket from lobby
            #-remove socket from listeningSockets list
            #-remove nickname from nickname list

        for sock in err:
            addr = sock.getpeername()
            self.remove_client(addr[0])
            self._lobby.remove(sock)
            self._listeningSockets.remove(sock)

        for sock in to_read:
            msg = []
            addr = sock.getpeername()
            msg.append(addr[0])
            while 1:
                buf = sock.recv(1024)
                #if not buf: break
                if buf.endswith(u"\r\n"):
                    msg.append(buf)
                    break
            
            print 'msg = ', msg
            self.parse_message(' '.join(msg))
        print 'leaving get_incoming_messages'

#ended writing the parse message function. Need to finish it and then decide how to handle 
#   either the command and/or broadcasting the message.
#   the format I have decided on for the messages are ip addr - current room - then either command/args or text
#   to broadcast to other users in same room.
    def parse_message(self, msg):
        print 'in parse_message'
        print 'msg being parsed = ', msg
        #parsed_msg[0] = ip addr
        #parsed_msg[1] = current room
        #the next parts could be: ([/command (arg)*]?)?(msg)*
        parsed_msg = msg.split()
        command_re = '/.'
        print 'parsed_mesage after msg.split()' , parsed_msg
        ip = parsed_msg[0]
        print 'ip = ', ip
        current_room = parsed_msg[1]
        print 'current_room = ', current_room
        #check if not a command then it needs to be broadcast to all of the users in the room
        if not re.match(command_re, parsed_msg[2]):
            if re.match('None', current_room):
                self.return_err(ip, current_room, self.NO_ROOM_ERR)
            else:
                self.broadcast_message(ip, current_room, ' '.join(parsed_msg[3:]))
        else:
            #join a room
            if re.match('/join', parsed_msg[2]):
                self.join_room(ip, ' '.join(parsed_msg[3:]))
            #leave current room
            elif re.match('/leave', parsed_msg[2]):
                self.leave_room(ip, current_room)
            #list all available rooms
            elif re.match('/list', parsed_msg[2]):
                self.list_rooms(ip, current_room)
            #leave all rooms and remove disconnect user
            elif re.match('/quit', parsed_msg[2]):
                self.purge_user(ip)
            else:
                #inform user of invalid command
                self.return_err(ip, current_room, parsed_msg[2] + COMMAND_ERR)
        print 'leaving parse_message'
    
    # This function broadcasts the message passed in to all of the other
    # users in the same room
    # return codes for client 100_incoming_message
    def broadcast_message(self, ip, curr_room, msg):
        print 'in broadcast'
        '''
        _clientsNick = dict() #hashes ip's to client nick
        _clientSockets = dict() #hashes ips to sockets
        _listeningSockets = [] #all of the sockets to be checked for incoming messages
        _rooms = dict() # hashes room names to list of ips in room
        _lobby = [] # list of client ip's that are not in a room. Any message
                    # input will return an error message until they join a room.
        '''
        #get the list of people in the same room
        message_str = self.INCOMING_MSG_CMD + ' ' + curr_room + ' <' + self._clientsNick[ip] + \
                        '> ' + msg  
        room_list = self._rooms[curr_room]
        #todo: need to check sockets before sending ********
        message_str_len = len(message_str)
        message_str = self.prep_message_to_send(message_str)
        for user in room_list:
            if user is not ip:
                sock = self._clientSockets[user]
                total_sent = 0
                while total_sent < message_str_len:
                    sent = sock.send(message_str)
                    total_sent += sent
        print 'leaving broadcast'
    
    #join_room
    #this function checks the _rooms data member to see if
    #the room has been created yet. If not it creates a room and
    # adds the user to the room. If yes then it adds the user to the
    # room and broadcasts to all other users that the new user has joined
    # the room.
    def join_room(self, ip, msg):
        print 'in join_room'
        print 'arg(msg) = ', msg
        if msg not in self._rooms:
            self._rooms[msg] = [ip]
        else:
            self._rooms[msg].append(ip)
        self._lobby.remove(ip)
        sock = self._clientSockets[ip]
        join_ack = self.prep_message_to_send(self.JOIN_ACK + ' ' + msg)
        print 'ack to client = ', join_ack
        sock.sendall(join_ack)
        self.broadcast_message(ip, msg, self.JOIN_MSG)
        print 'leaving join_room'        
        

    #def join_room(self, room_name):
    #def leave_room():
    #return_err(ip, current_room, NO_ROOM_ERR)

    def return_err(self, ip, room, error):
        print 'in return_err method'
        sock = self._clientSockets[ip]
        msg = prep_message_to_send(error)
        print 'message sent = ', msg
        sock.sendall(msg)
        print 'leaving return_err method'

    def prep_message_to_send(self, msg):
        print 'in prep_message_to_send'
        ready_to_send = msg + ' \r\n'
        print 'ready_to_send = ', ready_to_send
        return ready_to_send

    def clientSockets_dump(self):
        key_list = self._clientSockets.keys()
        if key_list is None:
            print 'empty socket list'
            return None
        else:
            return key_list

    def clientsNick_dump(self):
        key_list = self._clientsNick.keys()
        if key_list is None:
            print 'empty nickname list'
            return None
        else:
            for i in key_list:
                print self._clientsNick[i]
    
    def lobby_dump(self):
        if len(self._lobby) is 0:
            print 'empty list'
        else:
            print self._lobby

    def testClientsNickDump(self):
        self._clientsNick = {'1.2.1.2':'jimmy','3.1.2.3': 'ron'}
        self.clientsNick_dump()


    def testGetNewConnections(self):
        #self.start_keyboard_thread()
        connected_ips = []
        old_list = []
        print 'in testGetNewConnection before loop'
        for i in range(0,10):
            print 'in testGetNewConnetion in loop'
            #to_read, to_write, err = select(self._incomingSockets, self._outgoingSockets, self._errorSockets, 10)
    
            self.get_new_connections()
            print 'dumping connected sockets *****'
            connected_ips = self.clientSockets_dump()
            if cmp(old_list, connected_ips) is 0:
                print 'no new connections'
            else:
                print connected_ips
                old_list = connected_ips
            print ''
            print ''
            print 'dumping nicknames *****'
            self.clientsNick_dump()

        print 'dumping lobby *****'
        self.lobby_dump()
        
        




    def run(self):
        print 'entering run'
        while True:
            self.get_new_connections()
            self.get_incoming_messages()
        print 'leaving run'




if __name__ == '__main__':
    
    
    server = None
    server = ircServer(5000)
    server.run()
    '''
    try:
        server = ircServer(5000)
        try:
            #server.testClientsNickDump()
            #server.testGetNewConnections()
            #server.get_incoming_messages()
            server.run()
        except:
            print 'server run error: closing server'
            server.close()
    except:
        print 'server cannot be started'
    '''



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
