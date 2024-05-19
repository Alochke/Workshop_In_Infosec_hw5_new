#!/usr/bin/python3

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from os import open, write, close, O_WRONLY
from struct import pack, calcsize
from ipaddress import ip_address
import guesslang

MITM_STRUCT = '!LHLHH'
MITM_SIZE = calcsize(MITM_STRUCT)

def has_C_code(data: bytearray):
    print("Guess is: " + str(guesslang.Guess().scores(data.decode(errors='replace'))['C']))
    if guesslang.Guess().scores(data.decode(errors='replace'))['C'] > 1e-14:
        return True
    return False

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
                inp = bytearray()
                while True:
                    data1 = bytearray()
                    while True:
                        print('receiving response.')
                        inp = outsock.recv(4096)            
                        data1 += inp
                        if (not inp) or data1.endswith(b'\r\n'): 
                            break
                    try:
                        conn.sendall(data1)
                    except:
                        ...

                    if data1.lstrip().startswith(b'221') or (not inp):
                        print("exiting.")
                        break

                    if data2[:len(data2) - 2].strip().lower() == b'data' and data1.lstrip().startswith(b'354'):
                        # Getting mail content.
                        flag = True
                        data2 = bytearray()
                        while True:
                            print('receiving data.')
                            inp = conn.recv(4096)
                            data2 += inp
                            if (not inp) or (data2.endswith(b'.\r\n') and flag) or data2.endswith(b'\r\n.\r\n'): 
                                break
                            flag = False
                    else:
                        data2 = bytearray()
                        while True:
                            print('receiving command.')
                            inp = conn.recv(4096)
                            data2 += inp 
                            if (not inp) or data2.endswith(b'\r\n'): 
                                break
                    print(data2)
                    if has_C_code(data2):
                        print(b"C code detected.")
                        try:
                            conn.sendall(b'C code has been sent, terminating connection.')
                        except:
                            ...
                        break
                    try:
                        outsock.sendall(data2)
                    except:
                        ...
                    if not inp:
                        print("exiting.")
                        break
