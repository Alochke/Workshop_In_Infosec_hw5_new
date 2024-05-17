

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from os import open, write, close, O_WRONLY
from struct import pack, calcsize
from ipaddress import ip_address
from urllib.parse import parse_qsl

MITM_STRUCT = '!LHLHH'
MITM_SIZE = calcsize(MITM_STRUCT)
FORMAT = 'UTF-8'

def escape(data: str):
    returned = b''
    for c in data:
        # Escape special characters
        if c in b'&#;`|*?~<>^()[]{}$\\,\x0A\xFF':
            returned += b'\\'
        returned += c.to_bytes(1,'little',signed =False)
    return returned

def escape_val(data: bytearray, searched_key: bytearray):
    if data.find(b'\r\n\r\n') == -1:
        return data
    header = data[:data.find(b'\r\n\r\n') + 4]
    data = data[data.find(b'\r\n\r\n') + 4:]
    i = 1
    lst = parse_qsl(data, keep_blank_values = True, errors='ignore')
    for key, val in lst:
        if key == searched_key:
            val = escape(val)
        header += key + b'=' + val + (b'&' if i != len(lst) else b'')
        i += 1
    return header


def protect_CVE(data: bytearray):
    if data.startswith(b'POST /ajax/logging/clearlog.php'):
        data = escape_val(data, b'logfile')
    elif data.startswith(b'POST /ajax/openvpn/activate_ovpncfg.php') or data.startswith(b'POST /ajax/openvpn/del_ovpncfg.php'):
        data = escape_val(data, b'cfg_id')
    return data

while True:
    data = bytearray()
    insock = socket(AF_INET, SOCK_STREAM)
    with socket(AF_INET, SOCK_STREAM) as outsock:
        outsock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # TODO remove?
        outsock.bind(('10.1.2.3', 15))
        print('http socket bound')
        outsock.listen()
        conn, addr = outsock.accept()
        # print('connection established from '+str(addr))
        with conn:
            flag = False
            length = 0
            while True:
                # We have to change the algorithm here from hw4's implementation to support client side http traffic that contains data.
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
                        length = int(data[indx + 16 : indx + data[indx:].find(b'\r\n')].decode('UTF-8'))
                        flag = True
                find = data.find(b'\r\n\r\n')
                if find != 0 and len(data[find + 4:]) == length:
                    break
            # print(data)
            data = protect_CVE(data)
            # print(data)

            #if(addr[0]=='10.1.1.1'): #assume true to simplify
            insock.connect(('10.1.1.1',80))


            # Update mitm port in kernel
            (_,mitmport)=outsock.getsockname()
            mitmdriver=open('/sys/class/fw/conns/mitm', O_WRONLY)
            write(mitmdriver,pack(MITM_STRUCT,int(ip_address('10.1.1.1')),80,int(ip_address(addr[0])),addr[1],mitmport))
            close(mitmdriver)

            insock.sendall(data)    

# ---------------- HANDLE RESPONSE -----------------------
            data = bytearray()
            while True:
                print('receiving response header')
                inp = insock.recv(4096)            
                if not inp: break
                data += inp
            # print(data)
            conn.sendall(data)
            

    insock.close()
