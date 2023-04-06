import argparse
from socket import *
from threading import Thread
from datetime import datetime as dt
import json
import time

FINISH_TRACKER = 'finished'
ERROR_IN_TRACKER = 'error'
BUFFER_SIZE = 1024
HEART_BEAT_TIME = 120
MINUTE = 60

request_logs = []
file_maps = {}
file_sizes = {}
alive_time_table = {}

def handle_heartbeat():
    while True:
        peers = []
        file_peers = []
        for peer in alive_time_table.keys():
            if (dt.now() - alive_time_table[peer]).seconds > MINUTE:
                peers.append(peer)
                for file in file_maps.keys():
                    for i, host in enumerate(file_maps[file]):
                        if host == peer:
                            file_peers.append((file, i))
        for peer in peers:
            del alive_time_table[peer]
            print('disconnected ' + peer[0] + ':' + str(peer[1]))
        for file, peer_index in file_peers:
            del file_maps[file][peer_index]
        time.sleep(HEART_BEAT_TIME)
    
def run_heartbeat_tracker():
    new_thread_2 = Thread(target=handle_heartbeat)
    new_thread_2.start()

def handle_inputs():
    while True:
        input_line_arr = input().split(' ')
        cmd = input_line_arr[0]
        if cmd == 'file_logs':
            arg = input_line_arr[1]
            if arg == '-all':
                print('*** all ***')
                print(file_maps)
            else:
                fname = arg
                if fname in file_maps.keys():
                    print(file_maps[fname])
                else:
                    print('no such file')
        elif cmd == 'request':
            print(request_logs)
        else:
            print('ERROR_IN_TRACKER')


def run_input():
    new_thread = Thread(target=handle_inputs)
    new_thread.start()

def serialize(list_seeders: list, file_size: int):
    return json.dumps(obj=(list_seeders, file_size))

def handle_get_request(sender_address, message, server_socket):
        print('start get request')
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
        print('finish get request')
    
def handle_share_request(sender_address, message, server_socket:socket):
        _, file_name, file_size = message.split(' ')
        if file_name in file_maps.keys():
            if not sender_address in file_maps[file_name]:
                file_maps[file_name].append(sender_address)
        else:
            file_maps[file_name] = [sender_address]
        file_sizes[file_name] = file_size
        server_socket.sendto('OK'.encode(), sender_address)
        print(file_maps)

def handle_tracking_task(sender_address, message:str, server_socket:socket):
    cmd = message.split(' ')[0]
    if cmd == 'get':
        print('get request ...')
        handle_get_request(sender_address, message, server_socket)    
    elif cmd == 'alive':
        alive_time_table[sender_address] = dt.now()
        print('alive request received')
    elif cmd == 'share':
        print('share request ...')
        handle_share_request(sender_address, message, server_socket)
    elif cmd == 'success':
        _, file_name, receiver_address, sender_address = message.split(' ')
        if not receiver_address in file_maps[file_name]:
            file_maps[file_name].append(receiver_address)
        request_logs.append(message)
    elif cmd == 'failed':
        request_logs.append(message)
    else:
        print('error request')

def run_tracker(address:str):
    print('tracker is starting ...')
    ip, port = address.split(':')
    server_socket = socket(family=AF_INET, type=SOCK_DGRAM)
    server_socket.bind((ip, int(port)))
    while True:
        msg, sender_address = server_socket.recvfrom(BUFFER_SIZE)
        print('connected ' + sender_address[0] + ':' + str(sender_address[1]))
        new_thread = Thread(target=handle_tracking_task, args=(sender_address, msg.decode(), server_socket))
        new_thread.start()



parser = argparse.ArgumentParser()
parser.add_argument('address')
args = parser.parse_args()
address = args.address


run_input()

run_heartbeat_tracker()

run_tracker(address=address)