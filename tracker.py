from socket import *
from utils import parse_address

def handle_udp(inputs):
    local_addr = parse_address(inputs[1])
    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.bind(local_addr)
    while True:
        msg, client_addr = server_socket.recvfrom()
        server_socket.sendto(msg, client_addr)

input_line = input().split(' ')

if input_line[0] == 'tracker.exe':
    handle_udp(inputs=input_line)
elif input_line[0] == 'request' and input_line[1] == 'logs':
    pass
elif input_line[0] == 'file_logs':
    if input_line[1] == '-all':
        pass
    elif input_line[1] != '':
        pass
    else:
        pass
