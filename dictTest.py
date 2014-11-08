#!/etc/python

from socket import *

test = dict()

test['feet'] = (1111,2222)
test['beer'] = (3333,4444)
test['greed'] = (5555,6666)

print len(test)
print test['feet']
print test['beer']
print test['greed']

print 'tuple test'
t1 = test['feet']
t2 = test['beer']
t3 = test['greed']

print t2[1]

socket_list = []
sock = socket(AF_INET, SOCK_STREAM)

sock.bind(test['feet'])
print test['feet'][0]
        
