

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from os import open, write, close, O_WRONLY
from struct import pack, calcsize
from ipaddress import ip_address
from urllib.parse import quote, unquote

MITM_STRUCT = '!LHLHH'
MITM_SIZE = calcsize(MITM_STRUCT)
FORMAT = 'UTF-8'

def escape(data: str):
    returned = ""
    for c in data:
        # Escape special characters
        if c in '&#;`|*?~<>^()[]{}$\\,\x0A\xFF':
            returned.extend('\\')
        returned.append(c)
    return returned

def escape_val(data: bytearray, key: bytearray):
    indx = data.find(b'\r\n\r\n')
    if len(data[indx + 4:]) != 0:
        pair_loc = 0
        i = 1
        key_pairs = data[indx + 4:].split(b'&')
        for key_pair in key_pairs:
            print(key_pair)
            if key_pair[:key_pair.find(b'=')] == key:
                escaped = bytearray(escape(unquote(key_pair[len(key) + 1:].decode())).encode())
                data = data[:indx + 4 + pair_loc + len(key) + 1] + escaped + (b'&' if i != len(key_pairs) else b'')
                pair_loc = len(key) + len(escaped) + 2
            else:
                pair_loc += len(key_pair) + 1
            i += 1
    return data


def protect_CVE(data: bytearray):
    if data.startswith(b'POST /ajax/logging/clearlog.php'):
        data = escape_val(data, b'log_file')
    elif data.startswith(b'POST /ajax/openvpn/activate_ovpncfg.php') or data.startswith(b'POST /ajax/openvpn/del_ovpncfg.php'):
        data = escape_val(data, b'cfg_id')
    return data

while True:
    data = bytearray()
    insock = socket(AF_INET, SOCK_STREAM)
    with socket(AF_INET, SOCK_STREAM) as outsock:
        outsock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # TODO remove?
        outsock.bind(('10.1.2.3', 15))
        # print('http socket bound')
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
            data = protect_CVE(data)

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
