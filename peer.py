from socket import *
import argparse
from threading import Thread
import time, sched
import pickle
import random
import json

list_of_trackers = []
files = [];
BUFFER_SIZE = 1024

def run_client(address, tracker_address, file_name, method):
    handle_client(address, tracker_address, file_name, method)

def upload_file(connection, request, cli_address):
    if request.split(' ')[0] == 'download':
        file_name = request.split(' ')[1]
        if file_name in files:
            try:
                with open('./files/' + file_name, 'r') as f:
                    connection.send(f.read(BUFFER_SIZE).encode())
            except:
                connection.send('error file_load')
        else:
            print('we do not have this file')
            connection.send('error wrong_file'.encode())
    else:
        print('ruined request from ' + cli_address[0] + ':' + cli_address[1])
        connection.send('error wrong_syntax_request'.encode())
    connection.close()
    exit(0)

def send_udp_request(tracker_ip, tracker_port, ip, port, msg):
    client_socket = socket(AF_INET, SOCK_DGRAM)
    client_socket.bind((ip, int(port)))
    client_socket.sendto(msg.encode(), (tracker_ip, int(tracker_port)))
    if not (tracker_ip, tracker_port) in list_of_trackers:
        list_of_trackers.append((tracker_ip, tracker_port))
    result_msg, _ = client_socket.recvfrom(BUFFER_SIZE)
    client_socket.close()
    result_msg = result_msg.decode()
    return result_msg

def download_send_udp_request(tracker_ip, tracker_port, ip, port, msg):
    result_msg = send_udp_request(tracker_ip, tracker_port, ip, port, msg)
    if result_msg != 'FAILED':
        list_of_seeders_bytes, file_size = result_msg
        print('file_size = ' + file_size)
        list_of_seeders = json.loads(list_of_seeders_bytes)
        host_ip, host_port = random.sample(list_of_seeders, 1)
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.bind((ip, port))
        client_socket.connect((host_ip, host_port))
        client_socket.send('download ' + file_name)
        data, server_address = client_socket.recvfrom(BUFFER_SIZE)
        print('server address = ' + server_address[0] + ':' + server_address[1])
        data = data.decode()
        if not data.startswith('error'):
            try:
                with open('./downloads/'+file_name, 'w') as f:
                    f.write(data)
                    f.flush()
                    f.close
            except:
                print('error writing_file')
                client_socket.close()
                exit(-1)
        else:
            client_socket.close()
            print('error fail_in_downloading')
            exit(-1)
    else:
        print('error failed_track_file')
        exit(-1)
    
def upload_send_udp_request(tracker_ip, tracker_port, ip, port, msg):
    result_msg = send_udp_request(tracker_ip, tracker_port, ip, port, msg)    
    if result_msg == 'OK':
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind((ip, int(port)))
        server_socket.listen(5)
        while True:
            connection, client_address = server_socket.accept()
            while True:
                request, cli_address = connection.recvfrom(BUFFER_SIZE)
                request = request.decode()
                new_thread = Thread(target=upload_file, args=(connection, request, cli_address))
                new_thread.start()
    else:
        print('error registering_on_tracker')
        exit(-1)


def alive_report(ip, port, tracker_ip, tracker_port):
    msg = 'alive ' + ip + ' ' + port
    print('report')
    print(msg)
    send_udp_request(tracker_ip, tracker_port, ip, port, msg)

def handle_client(address:str, tracker_address:str, file_name:str, method:str):
    tracker_ip, tracker_port = tracker_address.split(':')
    ip, port = address.split(':')

    if method == 'get':
        download_send_udp_request(tracker_ip, tracker_port, ip, port, msg='get ' + file_name)

    elif method == 'share':
        upload_send_udp_request(tracker_ip, tracker_port, ip, port, 'share ' + file_name)
        
    else:
        print('ERROR')
        return

def handle_inputs():
    while True:
        print(list_of_trackers)

def heartbeat(my_ip, my_port):
    while True:
        time.sleep(10)
        for ip, port in list_of_trackers:
            alive_report(my_ip, my_port, ip, port)

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

new_thread = Thread(target=run_client, args=(address, tracker_address, file_name, method))
new_thread.start()

new_thread_2 = Thread(target=heartbeat, args=(ip, port))
new_thread_2.start()

handle_inputs()