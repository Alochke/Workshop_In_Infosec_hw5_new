#!/usr/bin/python3

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from os import open, write, close, O_WRONLY
from struct import pack, calcsize
from ipaddress import ip_address

MITM_STRUCT = '!LHLHH'
MITM_SIZE = calcsize(MITM_STRUCT)
    
while True:
    with socket(AF_INET, SOCK_STREAM) as insock:
        insock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # TODO remove?
        insock.bind(('10.1.1.3', 205))
        insock.listen()
        conn, addr = insock.accept()
        outsock = socket(AF_INET, SOCK_STREAM)
        outsock.connect(('10.1.2.2', 25))

        # Update mitm port in kernel
        (_,mitmport)=outsock.getsockname()
        mitmdriver=open('/sys/class/fw/conns/mitm', O_WRONLY)
        write(mitmdriver,pack(MITM_STRUCT,int(ip_address(addr[0])),addr[1],int(ip_address('10.1.2.2')),25,mitmport))
        close(mitmdriver)

        with conn:
            with outsock:
                data1, data2 = bytearray(), bytearray()
                while True:
                    data1 = bytearray()
                    while True:
                        print('receiving response.')
                        inp = outsock.recv(4096)            
                        data1 += inp
                        if not inp or data1.endswith(b''): 
                            break
                    conn.sendall(data1)

                    data2 = bytearray()
                    while True:
                        print('receiving command.')
                        inp = conn.recv(4096)            
                        if not inp or data2.endswith(b'\r\n'): 
                            break
                    conn.sendall(data2)

                    if not data1 and not data2:
                        break

