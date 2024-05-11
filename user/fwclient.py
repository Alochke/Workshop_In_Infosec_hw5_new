#!/usr/bin/python3

from sys import stdout, argv, exit
from os import open, read, O_RDONLY, O_WRONLY, close, write
from struct import pack, unpack, calcsize
from ipaddress import ip_address
from time import localtime, strftime
import builtins

# '!' means big-endian
RULE_STRUCT = '!20sIIIBIIBHHBIB'
RULE_SIZE = calcsize(RULE_STRUCT)
RULE_FORMAT = '%s %s %s %s %s %s %s %s %s\n'

DIRECTION_MAP = {0x01000000: 'in', 0x02000000: 'out', 0x03000000: 'any'}
PROTOCOL_MAP = {1:'ICMP', 6:'TCP', 17:'UDP', 143:'any'}
ACK_MAP = {0x01000000: 'no', 0x02000000: 'yes', 0x03000000: 'any'}
ACTION_MAP= {0:'drop', 1:'accept'}
REASON_MAP = {-1:'REASON_FW_INACTIVE', -2:'REASON_NO_MATCHING_RULE',
    -4:'REASON_XMAS_PACKET', -6:'REASON_ILLEGAL_VALUE'}

REV_DIR_MAP = {'in':0x01000000, 'out':0x02000000,'any':0x03000000}
REV_PROT_MAP ={'ICMP':1,'TCP':6,'UDP':17,'any':143}
REV_ACK_MAP={'no':0x01000000, 'yes':0x02000000,'any':0x03000000}
REV_ACTION_MAP={'drop':0,'accept':1}

# '=' means little-endian
LOG_STRUCT = '=LBB4s4s2s2siI'
LOG_SIZE = calcsize(LOG_STRUCT)
LOG_FORMAT = "%s\t%s\t%s\t%d\t%d\t%s\t%s\t%s\t%d\n"
LOG_HEADER = 'timestamp			src_ip			dst_ip			src_port	dst_port	protocol	action	reason				count'

CONN_STRUCT = '!IIHHHBLL'
CONN_SIZE = calcsize(CONN_STRUCT)
CONN_FORMAT = '%s:%d -> %s:%d at state %s\n'
TCPSTATE_CLMAP = ['SYN_SENT','SYN_SENT','ESTABLISHED', 'FIN_WAIT_1', 'FIN_WAIT_2', 'FIN_WAIT_2']
TCPSTATE_SVMAP = ['LISTEN', 'SYN_RECEIVED', 'ESTABLISHED', 'CLOSE_WAIT','CLOSE_WAIT','LAST_ACK']

def show_rules():
    rules=open('/sys/class/fw/rules/rules', O_RDONLY)    
    rulecount=int.from_bytes(read(rules,4),'little')
    for _ in range(rulecount):
        (name, direction, src_ip, _, src_prefix, dst_ip, _,
            dst_prefix, src_port, dst_port,
            protocol, ack, action) = unpack(RULE_STRUCT,read(rules, RULE_SIZE))
        src_ip_str=str(ip_address(src_ip))
        dst_ip_str=str(ip_address(dst_ip))
        src_ip_str+='/'+str(src_prefix)
        dst_ip_str+='/'+str(dst_prefix)
        src_ip_str= 'any' if src_ip_str=='0.0.0.0/0' else src_ip_str
        dst_ip_str= 'any' if dst_ip_str=='0.0.0.0/0' else dst_ip_str
        src_port_str = 'any' if src_port == 0 else '>1023' if src_port == 1023 else str(src_port)
        dst_port_str = 'any' if dst_port == 0 else '>1023' if dst_port == 1023 else str(dst_port)
        stdout.write(RULE_FORMAT % (name.decode().rstrip('\0'), DIRECTION_MAP[direction],
            src_ip_str, dst_ip_str, PROTOCOL_MAP[protocol],
            src_port_str, dst_port_str, ACK_MAP[ack], ACTION_MAP[action]))



def show_log():
    logs = open('/dev/fw_log', O_RDONLY)
    logcount=int.from_bytes(read(logs,4), 'little')
    print(LOG_HEADER)
    for _ in range(logcount):
        (timestamp,protocol,action,src_ip_bytes,dst_ip_bytes,
            src_port_bytes, dst_port_bytes, reason, count) = unpack(LOG_STRUCT, read(logs,LOG_SIZE))
        src_ip=int.from_bytes(src_ip_bytes,'big')
        dst_ip=int.from_bytes(dst_ip_bytes,'big')
        src_ip_str=str(ip_address(src_ip))
        dst_ip_str=str(ip_address(dst_ip))
        src_port=int.from_bytes(src_port_bytes,'big')
        dst_port=int.from_bytes(dst_port_bytes,'big')
        time=localtime(timestamp)
        timestr=strftime('%d/%m/%Y %H:%M:%S',time)
        reasonstr = REASON_MAP[reason] if reason < 0 else str(reason)
        stdout.write(LOG_FORMAT % (timestr, src_ip_str, dst_ip_str, src_port, dst_port,
            PROTOCOL_MAP[protocol].lower(), ACTION_MAP[action], reasonstr, count))
    close(logs)

def clear_log():
    cleardev=open('/sys/class/fw/log/reset',O_WRONLY)
    write(cleardev,b'x')
    close(cleardev)

def load_rules(rulepath):
    rulelist=[]
    with builtins.open(rulepath) as rulefile:
        rulelist=rulefile.readlines()
    rules = open('/sys/class/fw/rules/rules', O_WRONLY)
    rulebuff=bytearray()
    rulebuff.extend(len(rulelist).to_bytes(4,'little'))
    for rule in rulelist:
        (name, dir, sip, dip, prot, sp, dp, ack, action) = rule.split(' ')
        name=name[:20] # concat name
        sip = '0.0.0.0/0' if sip=='any' else sip
        dip = '0.0.0.0/0' if dip=='any' else dip
        sipstr, smask=sip.split('/')            
        dipstr, dmask=dip.split('/')
        sp = '0' if sp == 'any' else sp
        sp = '1023' if sp == '>1023' else sp
        dp = '0' if dp == 'any' else dp
        dp = '1023' if dp == '>1023' else dp
        binsip=int(ip_address(sipstr))
        bindip=int(ip_address(dipstr))
        action=action.rstrip()
        binrules=pack(RULE_STRUCT, name.encode(), REV_DIR_MAP[dir], binsip, 
            0, int(smask), bindip, 0, int(dmask), int(sp), int(dp), 
            REV_PROT_MAP[prot], REV_ACK_MAP[ack], REV_ACTION_MAP[action])
        rulebuff.extend(binrules)
    write(rules, rulebuff)
    close(rules)

def show_conns():
    conns = open('/sys/class/fw/conns/conns', O_RDONLY)
    conncount = int.from_bytes(read(conns,4),'little')
    for _ in range(conncount):
        (cl_ip, sv_ip, cl_port, sv_port, mitm_port,
         tcp_state, _, _) = unpack(CONN_STRUCT, read(conns, CONN_SIZE))
        clip_str=str(ip_address(cl_ip))
        svip_str=str(ip_address(sv_ip))
        stdout.write(CONN_FORMAT % (clip_str,cl_port,svip_str,sv_port,TCPSTATE_CLMAP[tcp_state]))
        stdout.write(CONN_FORMAT % (svip_str,sv_port,clip_str,cl_port,TCPSTATE_SVMAP[tcp_state]))
    close(conns)
    pass


def main():
    if len(argv) == 2:
        if argv[1] == 'show_rules':
            show_rules()
            exit(0)
        elif argv[1] == 'show_log':
            show_log()
            exit(0)
        elif argv[1] == 'clear_log':
            clear_log()
            exit(0)
        elif argv[1] == 'show_conns':
            show_conns()
            exit(0)
    if len(argv) == 3 and argv[1] == 'load_rules':
        load_rules(argv[2])
        exit(0)
    print('Invalid arguments')
    exit(1)
        

if __name__ == '__main__':
    main()