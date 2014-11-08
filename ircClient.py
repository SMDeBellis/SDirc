#!/etc/python
#Sean DeBellis copyright 2014
#IRC Program for cs494

from threading import *
import errno
import socket
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
    
