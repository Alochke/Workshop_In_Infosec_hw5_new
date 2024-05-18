#!/usr/bin/python3

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from os import open, write, close, O_WRONLY
from struct import pack, calcsize
from ipaddress import ip_address
from threading import Thread, Lock

MITM_STRUCT = '!LHLHH'
MITM_SIZE = calcsize(MITM_STRUCT)

class SockPlus(socket):
    lock = Lock()
    is_closed = False


    def factor(self, func):
        self.lock.acquire()
        if not self.is_closed:
            return func()
        self.lock.release()

    def close(self) -> None:
        self.lock.acquire()
        if not self.is_closed:
            self.is_closed = True
            self.socket.close()
        self.lock.release()


def handle(sock1: SockPlus, sock2: SockPlus):
    print('Started request thread')
    while True:
        data = bytearray()
        while True:
            inp = sock1.factor(lambda x: sock1.socket.recv(4096))
            if not inp:
                sock1.close()
                return
            data += inp
            if data.endswith(b'\r\n'): break # FTP command termination

        sock2.factor(lambda x: sock2.socket.sendall())


with socket(AF_INET, SOCK_STREAM) as insock:
    insock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # TODO remove?
    insock.bind(('10.1.1.3', 205))
    print('ftp socket bound')
    
    insock.listen()
    while True:        
        print('Waiting for connection')
        conn, addr = insock.accept()
        print('connection established from '+str(addr))     
                  
        outsock=socket(AF_INET, SOCK_STREAM)
        outsock.connect(('10.1.2.2',25))
        # Update mitm port in kernel
        (_,mitmport)=outsock.getsockname()
        mitmdriver=open('/sys/class/fw/conns/mitm', O_WRONLY)
        write(mitmdriver,pack(MITM_STRUCT,int(ip_address(addr[0])),addr[1],int(ip_address('10.1.2.2')),25,mitmport))
        close(mitmdriver)    

        sock1 = SockPlus()
        sock2 = SockPlus()
        sock1.socket = conn
        sock2.socket = outsock
        rqt=Thread(target=handle,args=(sock1, sock2))
        rpt=Thread(target=handle,args=(sock1, sock2))
        rqt.start()
        rpt.start()
                
