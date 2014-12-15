#!/etc/python
#Sean DeBellis copyright 2014 
#This is an IRC Server
#
from socket import *
from select import *
from threading import *
import re
import time
#command definitions:
#  * /nick - alias a name
#  * /list - lists all of the rooms
#  * /join - join a room 
#  * /leave - leave a room
#  * /quit - end irc session
#  * /members - lists all users in the current room

#  Incoming Message format -
#   ip, current room, command [, arg]* [, text]



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
#  11-16-14:
#   still working on getting the messages passed back and forth
#   I believe I have them sending from the client correctly but am
#   having trouble getting each message seperately from the socket.
#   the messages come across bunched up so the '\r\n' is not at the 
#   end of the message. I think I will need to keep a buffer for the 
#   reading and then parse up to the '\r\n'.
#
#   So I have added in buffers and out buffers to both the server
#   and client program. In the Server program I also added a function
#   called get_next_msg that if the in_buffer has a complete message 
#   defined as ending in \r\n, it will take it out of the in_buffer
#   and place it in the out_buffer to be delt with. This function
#   should be transferable as is to the client program as all buffers
#   have the same names. This function will be called in the send
#   functions for passing messages back and fourth between client and 
#   server. 
#
#   Next I need to rework the send_messages and get_messages functions
#   to work with the new buffers.
#
#   11-24-14:
#   After a bit of a struggle and confusion, I have gotten message formats 
#   solidified so that I can pass commands and messages to the server which then
#   passes back the correct reply/response. I have now completed /join
#   and broadcast message which passes a message to all of the users
#   that belong to the room. I still have to test with multiple users.
#   
#   TODO:
#       /nick
#
#   Ended at 1:00pm with the ability to change the nickname of the user
#   Have weird behavior in that it is skipping messages and i'm not sure
#   if its on the sending side or on the recieving side. More tests are needed.
#
#   Ended at 10pm I have reduced the wait on select in both the server and client
#   program to 1. There still seems to be an occasional problem where it seems t0
#   miss the join room and then when it goes into change name and then broadcast
#   there is a none error exception thrown when getting the room list to broadcast.
#   I also added an extra arg to broadcast so that I could stop self broadcast on
#   functions that don't need to (join, change_room)
# 
#   11-25-14
#   I have solved the missing log in problem by adding a bit of delay on the
#   clients side to ensure that they are not sending messages faster than the server can handle
#a  Have got the server and one client working with the configuration:
#   Config 1
#       Server : select 10, select 10 , socket nonblocking
#       Client : select 10, select 10 , socket nonblocking
#       Outcome Successful
#   Config 2
#       Server : select 10, select 10, socket nonblocking
#       Client : select 8,  select 8,  socket nonblocking
#       Outcome Failed
#   Config 3
#       Server: select 8, select 8, socket nonblocking
#       Client: select 8, select 8, socket nonblocking
#       Outcome Successful
#   Config 4
#       Server: select 1, select 1, socket nonblocking
#       Server: select 1, select 1, socket nonblocking
#       Outcome Successful but only with one client
#
#   It seems that with one client the server is in sync with it and
#   the timing is correct but once you throw a second one in it starts
#   losing messages. It could be because I have the loops in each of the 
#   clients the same. I may just impliment the keyboard input on the client
#   and then see if that solves the problem.
#
#   11-27-14(happy thanksgiving)
#   I have decided to set aside the issue of multiple users messages not
#   always getting missed and to finish implementing all of the minimal
#   features.
#   
#   Finished with /list
#   Need to test /leave
#   Tested /leave
#   Need to do return error for /leave when extra args are passed in
#
#   11-28-14
#   Finished error for /leave having extra arguments. I've decided
#   to handle all of the sending errors on the clients side as to not
#   burden the server with unneccessary work.
#   At this point I have finished all of the basic functionality of being 
#   able to create a room/ join a room which I kind of combined into the 
#   /join functionality as if the room isn't in existance when the room is
#   joined it is created at that time. There is no explicit create function.
#   Users can leave rooms and list all rooms. I still need to do the client
#   side program control loop as right now I am just calling the send_input and
#   receive from server 
#
#   11-29-14
#   Spent all of today trying to build a gui with curses but failed when
#   it came to getting user input in a way that didn't slow down the already
#   super slow working of this program... need more time.
#   
#   11-30-14
#   Need to finish data input for the client program.
#   Made a get input function that checks stdin using select
#   and then if select returns stdin in the read list then I read
#   in the string and return it, else I just return none.
#   Created the main run loop for the client program. It consists of 
#   the collection of user input, if it exists send it to the server, else
#   recieve from the server.
#   
#   fixes:
#   1. move all selects to 5
#
#   Need to finish:
#   Disconnecting from server - done
#   Disconnecting server from all clients 
#   Handling crashes from server to client and vice versa - done
#   Sending messages to multiple rooms 
#   
#*****************IMPORTANT**************************************
# All incoming messages will be in the form of 
#       'ip,roomname,msg \r\n'
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
    _in_buffer = []
    _out_buffer = []

    
    DUP_NICK_ERR = '301_command_error : nickname is already taken'
    INCOMING_MSG_CMD = '100_incoming_message'
    NICK_CHANGE_ACK = '200_nickname_change'
    NICK_MSG = 'has changed nickname to:'
    JOIN_ACK = '300_room_joined'
    JOIN_MSG = 'has joined the room'
    LIST_ROOM_CMD = '400_rooms_list' 
    LEAVE_ROOM_CMD = '500_leave_room'
    LEAVE_MSG = ' has left the room'
    LIST_MEMBERS_CMD = '700_members_list'
    

    def __init__(self, serverPort=5000):
        print 'in __init__'
        self._PORT = serverPort
        self._masterSocket = socket(AF_INET, SOCK_STREAM)
        self._masterSocket.bind((self._HOST , self._PORT ))
        self._masterSocket.listen(5)
        self._incomingSockets.append(self._masterSocket)

    def close(self):
        print 'closing all sockets'
        print 'server closing connection'
        socks = self._clientSockets.values()
        for sock in socks:
            sock.close()
        self._masterSocket.shutdown(SHUT_RDWR)
	self._masterSocket.close()

               
    #Checks the master socket for waiting connections and if they are present
    #   adds them to the list of client sockets
    #   it also calls a receive which must carry the hostname of the computer
    #   being logged on by.
    def get_new_connections(self):
        print 'calling get_new_connections'
        to_read, to_write, err = select(self._incomingSockets, self._outgoingSockets, self._errorSockets, 1)

        for sock in to_read:
            if sock == self._masterSocket:
                try:
                    conn, addr = sock.accept()
                except:
                    print 'error connecting'
                    return
                conn.setblocking(0)
                self._clientSockets[str(addr[1])] = conn
                try:
                    hostName = conn.recv(1024)
                except:
                    time.sleep(1)
                    hostName = conn.recv(1024)
                self._clientsNick[str(addr[1])] = hostName
                self._listeningSockets.append(conn)
                self._lobby.append(str(addr[1]))
        #print 'exiting get_new_connections'
    
    #get_next_msg
    #This function must move msgs from the in_buffer to the out_buffer and
    #   then signal if at least one msg has been moved
    #This function gets the next message from the in buffer concatinates it 
    # together if necessary and places it out buffer to be processed and 
    # delt with accordingly.
    # Returns 0 if buffer is empty or incomplete message, 1 if there was a message

    #***********important*************************
    #need to redo this function as it is adding extra
    #spaces onto the front of the string before going
    #to the out_buffer. I have patched it with a call
    #to strip() before sending it to be appended to the 
    #out_buffer.
    def get_ready_msgs(self):
        if self._in_buffer:
            msg = ''
            found = False
            count = 0
            for chunk in self._in_buffer:
                ndx = chunk.find('\r\n')
                if ndx == -1:
                    msg = msg + ' ' + chunk
                    count += 1
                else:
                    found = True
                    msg = msg + ' ' + chunk[:ndx+2]
                    chunk = chunk[ndx+4:]
                    break
            if found == True:
                self._in_buffer = self._in_buffer[count+1:]
                self._out_buffer.append(msg)
                return 1
            else:
                return 0
        else:
            return 0
       
    
    def remove_from_all_rooms(self, ip):
        room_lists = self._rooms.values()
        for room in room_lists:
            room.remove(ip)
    
    def remove_client(self, ip):
        self.remove_from_all_rooms(ip)
        del self._clientNick[ip]
        
    
    def get_incoming_messages(self):
        to_read, to_write, err = select(self._listeningSockets, [], self._listeningSockets, 1)
        
        #could be a possible error here, need to purge from all room lists
        for sock in err:
            addr = sock.getpeername()
            self.remove_client(addr[1])
            self._lobby.remove(sock)
            self._listeningSockets.remove(sock)

        for sock in to_read:
            try:
                buf = sock.recv(1024)
            except:
                print 'breaking in get_incoming connection due to exception'
                break
            if buf:#without this empty string was going into buffer
                self._in_buffer.append(buf)
                            
            while self.get_ready_msgs():
                pass
        #need to figure out how to get rid of the extra spaces       
        while self._out_buffer:
            self.parse_message(self._out_buffer[0].strip())
            del self._out_buffer[0]


#ended writing the parse message function. Need to finish it and then decide how to handle 
#   either the command and/or broadcasting the message.
#   the format I have decided on for the messages are ip addr - current room - then either command/args or text
#   to broadcast to other users in same room.
#   ****ALL ERROR FUNCTIONS MUST be in the form of error, room name, msg*****
    def parse_message(self, msg):
        print 'in parse message msg = ', msg
        parsed_msg = msg.split(',')
        command_re = '/.'
        ip = parsed_msg[0]
        current_room = parsed_msg[1]
        
        #check if not a command then it needs to be broadcast to all of the users in the room
        if not re.match(command_re, parsed_msg[2]):
            if re.match('None', current_room):
                self.return_err(ip, current_room, self.NO_ROOM_ERR)
            else:
                
                msg_to_send = ' '.join(parsed_msg[2:])
                self.broadcast_message(ip, current_room, msg_to_send.strip(), 0)
        else:
            #join a room
            #should come from client as:
                #ip,currentRoom,command,roomToJoin \r\n
            if re.match('/join', parsed_msg[2]):
                self.join_room(ip, self.strip_delimiter(','.join(parsed_msg[3:])))
            #change nickname
            #should come from client as:
                #ip,currentRoom,command,newNick \r\n
            elif re.match('/nick', parsed_msg[2]):
                self.change_nickname(ip, current_room, self.strip_delimiter(','.join(parsed_msg[3:])))
            #leave current room
            #should come from client as:
                #id,currentRoom,command \r\n
            elif re.match('/leave', parsed_msg[2]):
                self.leave_room(ip, current_room)
            #list all available rooms
            #should come from client as:
                #id,currentRoom,command \r\n
            elif re.match('/list', parsed_msg[2]):
                self.list_rooms(ip, current_room)
            #leave all rooms and remove disconnect user
            #should come from client as:
                #id,currentRoom, command \r\n
            elif re.match('/quit', parsed_msg[2]):
                self.purge_user(ip)
            #list all users in the room
            #should come from client as:
                #id,currentRoom,command \r\n
            elif re.match('/members', parsed_msg[2]):
                self.list_members(ip, current_room)

            else:
                #inform user of invalid command
                self.return_err(ip, current_room, parsed_msg[2] + COMMAND_ERR)

    
    # remove the user from all rooms broadcasting to the other users in the room that
    #   they have left and remove the socket from all lists and dictionaries 
    #   and then closes the socket
    def purge_user(self, ip):
        room_names = self._rooms.keys()
        for room in room_names:
            current_room = self._rooms[room]
            if ip in current_room:
                self.broadcast_message(ip, room, self.LEAVE_MSG, 1)
                current_room.remove(ip)
                self._rooms[room] = current_room
        if ip in self._lobby:
            self._lobby.remove(ip)
        if ip in self._clientsNick:
            del self._clientsNick[ip]
        if ip in self._clientSockets:
            sock = self._clientSockets[ip]
            if sock in self._listeningSockets:
                self._listeningSockets.remove(sock)
            del self._clientSockets[ip]
            sock.close()
        
        
    # This function broadcasts the message passed in to all of the other
    # users in the same room
    # return codes for client 100_incoming_message
    def broadcast_message(self, ip, curr_room, msg, flag):
        #get the list of people in the same room
        message_str = self.INCOMING_MSG_CMD + ',' + curr_room + ',' + self._clientsNick[ip] + ',' + msg  
        room_list = self._rooms[curr_room]
        #todo: need to check sockets before sending ********
        message_str_len = len(message_str)
        message_str = self.prep_message_to_send(message_str)
        for user in room_list:
            if user != ip or flag == 0:
                print 'user and ip', user, ip
                sock = self._clientSockets[user]
                total_sent = 0
                while total_sent < message_str_len:
                    sent = sock.send(message_str)
                    total_sent += sent
        
    
    #join_room
    #this function checks the _rooms data member to see if
    #the room has been created yet. If not it creates a room and
    # adds the user to the room. If yes then it adds the user to the
    # room and broadcasts to all other users that the new user has joined
    # the room.
    # TODO: need to make sure user cannot join the same room multiple times
    #       make it so None cannot be a room name
    def join_room(self, ip, msg):
        if msg not in self._rooms:
            self._rooms[msg] = [ip]
        else:
            self._rooms[msg].append(ip)
        if ip in self._lobby:
            self._lobby.remove(ip)
        sock = self._clientSockets[ip]
        join_ack = self.prep_message_to_send(self.JOIN_ACK + ',' + msg)
        #print 'join_ack = ', join_ack
        sock.sendall(join_ack)
        join_relay = self._clientsNick[ip] + ' ' + self.JOIN_MSG
        self.broadcast_message(ip, msg, join_relay, 1)
    
    

    def change_nickname(self, ip, room, new_name):
        #print 'in change_nickname room = ', room 
        all_nicks = self._clientsNick.values()
        if new_name in all_nicks:
            self.return_err(ip, room, self.DUP_NICK_ERR)
        else:
            old_nick = self._clientsNick[ip]
            self._clientsNick[ip] = new_name
            nick_ack = self.prep_message_to_send(self.NICK_CHANGE_ACK + ',' + new_name)
            sock = self._clientSockets[ip]
            sock.sendall(nick_ack)
            if room is 'None':
                self.broadcast_message(ip, room, old_nick + ' ' + self.NICK_MSG + ' ' + new_name, 1)

    
    #msg = code,room,{room | 'None'} [,room]*
    def list_rooms(self, ip, current_room):
        msg = self.LIST_ROOM_CMD + ',' + current_room
        room_list = self._rooms.keys()
        if not room_list:
            msg = msg + ',None'    
        else:
            for room in room_list:
                msg = msg + ',' + room
        msg = self.prep_message_to_send(msg)
        sock = self._clientSockets[ip]
        sock.sendall(msg)

    
    # lists all of the members in the current room 
    #   of the given ip of the client
    def list_members(self, ip, current_room):
        msg = self.LIST_MEMBERS_CMD + ',' + current_room
        room = self._rooms[current_room]
        if not room:
            msg = msg + ',None'
        else:
            for user in room:
                msg = msg + ',' + self._clientsNick[user]
        
        msg = self.prep_message_to_send(msg)
        sock = self._clientSockets[ip]
        sock.sendall(msg)



    #msg = code, room 
    def leave_room(self, ip, room):
        room_list = self._rooms[room]
        room_list.remove(ip)
        self._rooms[room] = room_list
        if not self.has_room(ip):
            self._lobby.append(ip)
        msg = self.LEAVE_ROOM_CMD + ',' + room
        msg = self.prep_message_to_send(msg)
        #need to send LEAVE_ROoM_CMD
        sock = self._clientSockets[ip]
        sock.sendall(msg)        
        #need to broadcast LEAVE ROOM MSG
        self.broadcast_message(ip, room, self._clientsNick[ip] + self.LEAVE_MSG, 0)

    def has_room(self,ip):
        rooms = self._rooms.values()
        for room in rooms:
            if ip in room:
                return True
        return False

    
    def return_err(self, ip, room, error):
        #print 'in return_err method'
        sock = self._clientSockets[ip]
        msg = self.prep_message_to_send(error + ',' + room)
        #print 'message sent = ', msg
        sock.sendall(msg)
        #print 'leaving return_err method'

    def strip_delimiter(self, msg):
        return re.sub(' \\r\\n', '', msg)

    def prep_message_to_send(self, msg):
        if re.match('(.)*\\r\\n$', msg) is None:
            ready_to_send = msg + ' \r\n'
        else:
            ready_to_send = msg
        return ready_to_send



    def run(self):
        print 'entering run'
        count = 0
        while True:
            self.get_new_connections()
            self.get_incoming_messages()
            
        print 'leaving run'




if __name__ == '__main__':
    
    
    server = None
    server = ircServer(5000)
    try:
        server.run()
    except:
        print 'Exception caught from run(): closing server'
        server.close()


##############################End Program######################################











#############################Test Code########################################

    '''
    #testing strip_delimeter
    print 'testing strip_delimeter: ', server.strip_delimiter('this is a test \r\n')

    
    #testing prep_message_to_send
    test1 = 'this is a test'
    test2 = 'this is a test \r\n'

    print 'test1 = this is a test = ', server.prep_message_to_send(test1)
    print 'test2 = this is a test \\r\\n = ', server.prep_message_to_send(test2)
    
    
    #testing get_ready_msgs()
    print 'testing empty buffer'
    server.get_ready_msgs()
    

    server._in_buffer.append('this is a test')
    server._in_buffer.append('here is an end \r\n')
    server._in_buffer.append('this is not ended and will remain')
    print 'testing filled buffer'
    print 'in_buffer before get_ready_msgs = ', server._in_buffer
    server.get_ready_msgs()
    print 'in_buffer after get_ready_msgs() = ', server._in_buffer
    print 'out_buffer after get_ready_msgs() = ', server._out_buffer
    '''
    








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
