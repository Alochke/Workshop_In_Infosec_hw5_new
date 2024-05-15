

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from os import open, write, close, O_WRONLY
from struct import pack, calcsize
from ipaddress import ip_address
import guesslang

MITM_STRUCT = '!LHLHH'
MITM_SIZE = calcsize(MITM_STRUCT)
FORMAT = 'UTF-8'

def has_wrong_type(data):
    header = data.split(b'\r\n\r\n')[0]
    header_lines = header.split(b'\r\n')
    for line in header_lines:
        if b'Content-type: text/csv' in line or b'Content-type: application/zip' in line:
            return True
    return False

def has_C_code(data: bytearray):
    if guesslang.Guess().scores(data.decode(FORMAT))['C'] > 1e-12:
        return True
    return False
    
    

while True:
    data = bytearray()
    outsock = socket(AF_INET, SOCK_STREAM)
    with socket(AF_INET, SOCK_STREAM) as insock:
        insock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # TODO remove?
        insock.bind(('10.1.1.3', 800))
        print('http socket bound')
        insock.listen()
        conn, addr = insock.accept()
        print('connection established from '+str(addr))
        with conn:
            flag = False
            length = 2
            while True:
                # We have to change the algorithm here compared from hw4's implementation to support client side http traffic that contains data.
                print('receiving request')
                inp = conn.recv(4096)
                if not inp: break
                data += inp
                if not flag:
                    indx = data.find(b'Content-Length:')
                    if indx != -1:
                        while data[indx:].find(b'\r\n') == -1:
                            inp = conn.recv(4096)            
                            if not inp: break
                            data += inp
                        print(data[indx:].decode('UTF-8'))
                        print(data[indx + 17 : data[indx:].find(b'\r\n')])
                        print(data[indx + 17 : data[indx:].find(b'\r\n')].decode('UTF-8'))
                        print(data[indx + 17 :])
                        print(data[data[indx:].find(b'\r\n'):].decode('UTF-8'))
                        length = int(data[indx + 17 : data[indx:].find(b'\r\n')].decode('UTF-8'))
                        flag = True
                find = data.find(b'\r\n\r\n')
                print("find: " + str(find))
                print("len: " + str(length))
                if find != 0 and len(data[find + 2 :]) == length:
                    break

            print(data) # for debug
            if(has_C_code(data)):
                print('\nC code detected!\n')
                outsock.close()
                continue

            #if(addr[0]=='10.1.1.1'): #assume true to simplify
            outsock.connect(('10.1.2.2',80))

            # Update mitm port in kernel
            (_,mitmport)=outsock.getsockname()
            mitmdriver=open('/sys/class/fw/conns/mitm', O_WRONLY)
            write(mitmdriver,pack(MITM_STRUCT,int(ip_address(addr[0])),addr[1],int(ip_address('10.1.2.2')),80,mitmport))
            close(mitmdriver)

            outsock.sendall(data)    

# ---------------- HANDLE RESPONSE -----------------------
            data = bytearray()
            while True:
                print('receiving response header')
                inp = outsock.recv(4096)            
                if not inp: break
                data += inp
            if(not has_wrong_type(data)):
                conn.sendall(data)
            else:
                print('\nProhibited type!\n')
            print(data)
            

    outsock.close()
