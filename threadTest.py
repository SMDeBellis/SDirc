from threading import *
from sys import *
from time import *
buf = [None]

def keyboard_input(input_buffer):
    
    while 1:
        buf[0] = raw_input()

mythread = Thread(target=keyboard_input, args=(buf))
mythread.daemon = True
mythread.start()
print 'enter input: '

while 1:
      
    #for increment in range(1,10):
    #    sleep(1)
    if buf[0] is not None:
        print buf[0]
        print 'enter input: '
        buf[0] = None





