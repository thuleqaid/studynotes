#!/usr/bin/python
import socket
import sys

def get_ip_addr(ifname='eth0'):
    ip=''
    import platform
    sysos=platform.system()
    if sysos=='Linux':
        import socket,fcntl,struct
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        f=fcntl.ioctl(s.fileno(),0x8915,struct.pack('256s',ifname[:15]))
        ip=socket.inet_ntoa(f[20:24])
    elif sysos=='Windows':
        import socket
        ip=socket.gethostbyname(socket.gethostname())
    return ip

if len(sys.argv)>1:
    hostip=get_ip_addr()
    lastidx=hostip.rfind('.')
    remoteip=hostip[0:lastidx]+'.1'

    HOST,PORT=remoteip,9999
    data=sys.argv[1]
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        sock.connect((HOST,PORT))
        sock.sendall(data)
    finally:
        sock.close()

