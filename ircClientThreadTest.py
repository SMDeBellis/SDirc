from threading import *
from socket import *
from time import *

HOST = '127.0.0.1'
PORT = 5000

def socket_thread():
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((HOST,PORT))
    
    sleep(20)

    sock.close()


for i in range(0, 10):
    t = Thread(target=socket_thread)
    t.start()
    


