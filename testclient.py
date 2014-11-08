#!/etc/python
from socket import *
import time

HOST = '10.0.0.6'
PORT = 5000

sock = socket(AF_INET, SOCK_STREAM)
sock.connect((HOST,PORT))

while(1):
    time.sleep(20)
    #sock.sendall('dude')
    #data = sock.recv(1024)
    #print 'Recieved: ', repr(data)
