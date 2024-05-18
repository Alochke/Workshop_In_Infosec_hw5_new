

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from os import open, write, close, O_WRONLY
from struct import pack, calcsize
from ipaddress import ip_address
import guesslang

MITM_STRUCT = '!LHLHH'
MITM_SIZE = calcsize(MITM_STRUCT)

while True:
    data = bytearray()
    outsock = socket(AF_INET, SOCK_STREAM)
    with socket(AF_INET, SOCK_STREAM) as insock:
        insock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # TODO remove?
        insock.bind(('10.1.1.3', 205))
        print('http socket bound')
        insock.listen()
        conn, addr = insock.accept()
        print('connection established from '+str(addr))
        with conn:
            while True:
                print('receiving request')
                inp = conn.recv(4096)            
                if not inp: break
                data += inp
                if data.endswith(b'\r\n'):
                    break

            # print(data) # for debug

            #if(addr[0]=='10.1.1.1'): #assume true to simplify
            outsock.connect(('10.1.2.2',25))


            # Update mitm port in kernel
            (_,mitmport)=outsock.getsockname()
            mitmdriver=open('/sys/class/fw/conns/mitm', O_WRONLY)
            write(mitmdriver,pack(MITM_STRUCT,int(ip_address(addr[0])),addr[1],int(ip_address('10.1.2.2')),25,mitmport))
            close(mitmdriver)

            outsock.sendall(data)    

# ---------------- HANDLE RESPONSE -----------------------
            data = bytearray()
            while True:
                print('receiving response header')
                inp = outsock.recv(4096)            
                if not inp: break
                data += inp
            

    outsock.close()
