#!/usr/bin/python3

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from os import open, write, close, O_WRONLY
from struct import pack, calcsize
from ipaddress import ip_address
from threading import Thread, Lock

MITM_STRUCT = '!LHLHH'
MITM_SIZE = calcsize(MITM_STRUCT)

def handlerequests(conn: socket, outsock: socket):
    print('Started request thread')
    while True:
        data = bytearray()
        while True:
            inp = conn.recv(4096)            
            if not inp: break
            data += inp
            if b'\r\n' in inp: break # FTP command termination
        print('request data:')        
        print(data)

        outsock.sendall(data)


        if data.startswith(b'PORT'):            
            print('PORT command identified')
            addr=data.rstrip().split(b' ')[1].split(b',')
            print(addr)
            port=(int(addr[4])<<8)+int(addr[5])
            print(port)
            ftpdriver=open('/sys/class/fw/conns/ftp',O_WRONLY)
            write(ftpdriver,port.to_bytes(2,'big'))
            close(ftpdriver)    
            print('\x1b[34msent port %d to kernel\x1b[m' % port)

def handleresponses(conn: socket, outsock: socket):
    print('Started response thread')
    while True:

        data = bytearray()
        while True:
            inp = outsock.recv(4096)            
            if not inp: break
            data += inp                
            if inp.endswith(b'\r\n'): break # FTP command termination                
        print('response data:')
        print(data)

        conn.sendall(data)              

with socket(AF_INET, SOCK_STREAM) as insock:
    insock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # TODO remove?
    insock.bind(('10.1.1.3', 210))
    print('ftp socket bound')
    
    insock.listen()
    while True:        
        print('Waiting for connection')
        conn, addr = insock.accept()
        print('connection established from '+str(addr))    
        #with conn:  
                  
        outsock=socket(AF_INET,SOCK_STREAM)
        outsock.connect(('10.1.2.2',21))
        # Update mitm port in kernel
        (_,mitmport)=outsock.getsockname()
        mitmdriver=open('/sys/class/fw/conns/mitm', O_WRONLY)
        write(mitmdriver,pack(MITM_STRUCT,int(ip_address(addr[0])),addr[1],int(ip_address('10.1.2.2')),21,mitmport))
        close(mitmdriver)    

        inlk=Lock()
        outlk=Lock()
        rqt=Thread(target=handlerequests,args=(conn, outsock))
        rpt=Thread(target=handleresponses,args=(conn, outsock))
        rqt.start()
        rpt.start()
                
