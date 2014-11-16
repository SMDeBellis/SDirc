#!/etc/python
#Sean DeBellis copyright 2014
#IRC Program for cs494

from threading import *
import errno
import socket
import sys
import re
from select import *

class ircClient:
    _host = None
    _port = None
    _nickname = None 
    _current_room = None
    _room_list = []
    _sock = None

    def __init__(self, server_ip, server_port):
        self._host = server_ip
        self._port = server_port
        self.nickname = socket.gethostname()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._sock.connect((self._host, self._port))
        except socket.error:
            sys.exit(socket.error[1])
        self._sock.sendall(self.nickname)

    # messages must be sent to server in this format:
    #   'current room' 'messsage'
    # current room may be none
    def send_input(self, msg):
        print 'entering send_input'
        to_read, to_write, err = select([], [self._sock], [], 10)
        msg_to_send = self.prep_message_to_send(str(self._current_room) + ' ' + msg)
        msg_length = len(msg_to_send)
        total_sent = 0
        print 'msg_to_send = ', [msg_to_send]
        if len(to_write) is not 0:
            while total_sent < msg_length:
                print 'sending message'
                sent = self._sock.send(msg_to_send)
                total_sent = total_sent + sent
            print 'message sent'
        print 'leaving send_input'

    def receive_from_server(self):
        print 'entering receive_from_server'
        to_read, to_write, err = select([self._sock], [], [], 10)
        buf = []
        if len(to_read) is not 0:
            count = 0
            while True:
                chunk = self._sock.recv(1024)
                print 'chunk = ', [chunk.split('\r\n')], ' count = ' + str(count)
                if chunk.endswith(u"\r\n"):
                    buf.append(chunk)
                    break
                else:
                    buf.append(chunk)
                count += 1

            print 'buf= ', buf
            print 'right before self.parse_iincoming()'
            self.parse_incoming(' '.join(buf))
            print 'right after self.parse_incoming()'
        
        print 'leaving receive_from_server'

#my idea for right now is to send any and all messages to the server and let it parse 
# the message and then do actions on the client side dependent upon the return message
# coming from the server.
#   Incoming message from server format:
#       'instruction code' 'room to post to' 'message'
#   Server Codes:                   Error Codes:
#       100_incoming_message            101_room_error   
#       200_incoming_private            201_command_error
#       300_room_joined
    def parse_incoming(self, msg):
        print 'entering parse_incoming w/ msg = ', msg
        parsed_msg = msg.split()
        code = parsed_msg[0] # get the command code
        room = parsed_msg[1] # get the room
        if re.match('100.', code):
            print ' '.join(parsed_msg)
        elif re.match('300.', code):
            self._current_room = ' '.join(parsed_msg[1:])
            print 'self._current_room = ', self._current_room
            print 'you have joined ' + room

        print 'leaving parse_incoming'


    def prep_message_to_send(self, msg):
        ready_to_send = msg + ' \r\n'
        return ready_to_send

if __name__ == '__main__':
    client = ircClient('127.0.0.1', 5000)
    print 'calling send_input to join room'
    client.send_input('/join dude room')
    
    while True:
        print ''
        print ''
        print 'in main calling receive_from_server()'
        client.receive_from_server()
        print 'in main after calling receive_from_server()'
        print ''
        print ''
        print 'in main calling send_input()'
        client.send_input('this is a test message')
        


'''
HOST = '127.0.0.1'#'10.0.0.6'#'24.20.80.232'
PORT = 5000

keyboard_buf = None
sock_buf = []

#
#This function continuously gets input from the
#   keyboard and stores it into a buffer.
def keyboard_input():
    while 1:
        keyboard_buf = raw_input('--> ')
        print keyboard_buf


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect((HOST,PORT))
    sock.sendall(socket.gethostname())  #send computer name for
                                        #initial nick
except socket.error:
    print 'connection with server nota vailable'

keyboard_thread = Thread(target=keyboard_input)
keyboard_thread.daemon = True
keyboard_thread.start()
'''

''' Got the keyboard input thread working. Have some concerns over 
concurrency of the keyboard_buf buffer. May need to use a lock to ensure
that there is no writting to the buffer from stdin while the data is
being sent by the socket. 

Next I need to deal with the receiveing of data across the socket.
My idea is to, in the loop, the first thing to do is check the socket
to see if there is any data and display that to the screen

The very first thing I have to do before the loop is to send the server
the hostname of the computer as it is waiting on it after the initial 
connection to add to the nickname of the computer.

'''
'''
while True:
    while True:                         #get any data sent in from the
        chunk = sock.recv(1024)         #server
        if not chunk:
            break
        else:
            sock_buf.append(chunk)
    print ''.join(sock_buf)

    if keyboard_buf is not None:
        msg_length = len(keyboard_buf)
        total_sent = 0
        while total_sent < msg_length:
            sent = sock.send(keyboard_buf[total_length:])
            total_sent = total_sent + sent
        keyboard_buf = None
'''
'''
#**
#This function continuously checks the socket for incoming 
#   messages from the server and when present writes
#   them out to the display
#def read_write_incoming(read_socket, socket_buffer):
#    print 'in read_write_incoming'
#    while 1:
#        print 'in loop'
#        print repr(read_socket)
#        socket_buffer[0] = read_socket.recv(1024)
#        print 'after recv'
#        if socket_buffer[0] is not None:
#            write_to_screen(socket_buffer[0])
#            sock_buffer[0] = None

def write_to_screen(msg):
    print msg

#make connection to server
sock = socket(AF_INET, SOCK_STREAM)
try:
    sock.connect((HOST,PORT))
except error:
    print 'whoops'
    #print 'connection with server not available'

#create and start thread to get keyboard_input
keyboard_thread = Thread(target=keyboard_input)
keyboard_thread.daemon = True
keyboard_thread.start()

#insert socket reading args in list to send to thread
display_args = [sock, sock_buf]

#create and start thread to monitor socket for incomming messages
#socket_monitor = Thread(target=read_write_incoming, args=display_args)
#socket_monitor.daemon = True
#socket_monitor.start()

while True:
    if keyboard_buf is not None:
        sock.sendall(keyboard_buf)
        keyboard_buf = None
    
    sock_buf = sock.recv(1024)
    if sock_buf is not None:
        print sock_buf
'''
    
