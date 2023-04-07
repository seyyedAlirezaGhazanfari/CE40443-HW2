from socket import *
import argparse
from threading import Thread
import os
from peer_downloader import download_send_udp_request
from peer_uploader import upload_send_udp_request
from utils import heartbeat

files = []
request_logs = []

FILE_DIR = './files/'
    



def handle_client(address:str, tracker_address:str, file_name:str, method:str):
    tracker_ip, tracker_port = tracker_address.split(':')
    ip, port = address.split(':')

    if method == 'get':
        download_send_udp_request(request_logs, tracker_ip, tracker_port, ip, port, 'get ' + file_name, file_name, files)

    elif method == 'share':
        path = FILE_DIR + file_name
        if not os.path.exists(path):
            print('no such file')
            return
        upload_send_udp_request(request_logs, tracker_ip, tracker_port, ip, port,
                                'share ' + file_name + ' ' + str(os.stat(FILE_DIR + file_name).st_size),
                                file_name, files
                                )
        
    else:
        print('ERROR')
        return

def handle_inputs():
    while True:
        cmd = input().split(' ')
        if cmd[0] == 'request' and cmd[1] == 'logs':
            print(request_logs)
        elif cmd[0] == 'finish':
            return
        else:
            print('error in command')



parser = argparse.ArgumentParser()
parser.add_argument('method')
parser.add_argument('file_name')
parser.add_argument('tracker_address')
parser.add_argument('address')
args = parser.parse_args()
address = args.address
file_name = args.file_name
method = args.method
tracker_address = args.tracker_address

ip, port = address.split(':')

new_thread = Thread(target=handle_inputs)
new_thread.start()


handle_client(address, tracker_address, file_name, method)

