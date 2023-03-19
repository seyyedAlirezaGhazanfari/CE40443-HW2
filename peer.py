from socket import *
from utils import parse_address

def send_request_to_tracker(msg, tracker_addr):
    client_socket = socket(AF_INET, SOCK_DGRAM)
    client_socket.sendto(msg, tracker_addr)
    res_msg, server_addr = client_socket.recvfrom()
    client_socket.close()
    return res_msg

def add_to_tracker_seeders(listen_addr, tracker_addr, fname):
    msg = ''
    return send_request_to_tracker(msg, tracker_addr)

def find_suitable_seeder(listen_addr, tracker_addr, fname):
    msg = ''
    return send_request_to_tracker(msg, tracker_addr)


input_line = input().split(' ')
method = input_line[1]
fname = input_line[2]
tracker_ip, tracker_port = parse_address(input_line[3])
listen_ip, listen_port = parse_address(input_line[4])

if method == 'share':
    pass
elif method == 'get':
    pass
else:
    pass