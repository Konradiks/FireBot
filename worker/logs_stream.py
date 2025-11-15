import socket
import time
from socketserver import UDPServer

ip = ""
ip = "192.168.1.101"
port = 514
buffer_size = 4096

UDPServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

UDPServer.bind((ip, port))

print("UDP Server listening on %s:%d" % (ip, port))

while True:
    data, addr = UDPServer.recvfrom(buffer_size)
    print("Received data from %s:%d" % (addr[0], addr[1]), end=" ")
    mess = data.decode().strip()
    print(data)
    print("Message: '" + mess +'"')
    print(type(data.decode()))
    if mess == 'exit':
        UDPServer.close()
        break
    time.sleep(1)

print("SERVER SHUTDOWN")

