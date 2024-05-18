#!/usr/bin/python3

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from os import open, write, close, O_WRONLY
from struct import pack, calcsize
from ipaddress import ip_address
from threading import Thread

MITM_STRUCT = '!LHLHH'
MITM_SIZE = calcsize(MITM_STRUCT)
    
    

def handle(sock1: socket, sock2: socket):
    print('Started request thread')
    data = bytearray()
    while True:
        inp = sock1.recv()
        if not inp:
            sock1.close()
            return
        data += inp
        if data.endswith(b'\r\n'): break # FTP command termination

    try:
        sock2.sendall(data)
    except:
        ...


with socket(AF_INET, SOCK_STREAM) as insock:
    insock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # TODO remove?
    insock.bind(('10.1.1.3', 205))
    print('smtp socket bound')
    
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

        rqt=Thread(target=handle,args=(conn, outsock))
        rpt=Thread(target=handle,args=(outsock, conn))
        rqt.start()
        rpt.start()
                
