import argparse
from socket import *
from threading import Thread
import time
from datetime import datetime as dt
import json

FINISH_TRACKER = 'finished'
ERROR_IN_TRACKER = 'error'
BUFFER_SIZE = 1024

request_logs = {}
file_logs = {}
file_maps = {}
file_sizes = {}
alive_time_table = {}
get_logs = []

class GetRequest:
    def __init__(self, sender, message, response) -> None:
        self.sender = sender
        self.message = message
        self.response = response

    def set_response(self, response:str):
        self.response = response

def serialize(list_seeders: list, file_size: int):
    return json.dumps(obj=(list_seeders, file_size))

def handle_get_request(sender_address, message, server_socket):
        print('start get request')

        request = GetRequest(sender_address, message, '') 
        _, file_name = message.split(' ')
        msg = ''
        if file_name in file_maps.keys():
            seeders = file_maps[file_name]
            file_size = file_sizes[file_name]
            msg = serialize(seeders, file_size).encode()
            server_socket.sendto(msg, sender_address)
        else:
            msg = 'error no_file'
            print(file_maps)
            server_socket.sendto(msg.encode(), sender_address)
        request.set_response(msg)
        get_logs.append(request)
        print('finish get request')
    
def handle_share_request(message, server_socket:socket):
        _, file_name, file_size, sender_address_str = message.split(' ')
        sender_address = (sender_address_str.split(':')[0], int(sender_address_str.split(':')[1]))
        if file_name in file_maps.keys():
            file_maps[file_name].append(sender_address)
        else:
            file_maps[file_name] = [sender_address]
        file_sizes[file_name] = file_size
        server_socket.sendto('OK'.encode(), sender_address)
        print(file_maps)

def handle_tracking_task(sender_address, message:str, server_socket:socket):
    cmd = message.split(' ')[0]
    if cmd == 'get':
        handle_get_request(sender_address, message, server_socket)    
    elif cmd == 'alive':
        alive_time_table[sender_address] = dt.now()
    elif cmd == 'share':
        handle_share_request(message, server_socket)
    else:
        print('error request')

def run_tracker(address:str):
    ip, port = address.split(':')
    server_socket = socket(family=AF_INET, type=SOCK_DGRAM)
    server_socket.bind((ip, int(port)))
    while True:
        msg, sender_address = server_socket.recvfrom(BUFFER_SIZE)
        new_thread = Thread(target=handle_tracking_task, args=(sender_address, msg.decode(), server_socket))
        new_thread.start()

def handle_heartbeat():
    while True:
        time.sleep(120)
        for peer in alive_time_table.keys():
            if (dt.now() - alive_time_table[peer]).seconds > 60:
                alive_time_table.pop(peer)
                for file in file_maps.keys():
                    indices = []
                    for i, host in enumerate(file_maps[file]):
                        if host == peer:
                            indices.append(i)
                for j in indices:
                    del file_maps[file][j]

def handle_inputs():
    while True:
        input_line_arr = input().split(' ')
        cmd = input_line_arr[0]
        if cmd == 'file_logs':
            arg = input_line_arr[1]
            if arg == '-all':
                print('*** all ***')
                pass
            else:
                fname = arg
        else:
            print(ERROR_IN_TRACKER)

parser = argparse.ArgumentParser()
parser.add_argument('address')
args = parser.parse_args()
address = args.address
new_thread = Thread(target=handle_inputs)
new_thread.start()
new_thread_2 = Thread(target=handle_heartbeat)
new_thread_2.start()
run_tracker(address=address)