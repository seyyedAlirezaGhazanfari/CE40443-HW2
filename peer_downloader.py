from socket import *
import random
from utils import BUFFER_SIZE, send_udp_request, run_file_sharing_server, send_udp_request_without_resp
import json

DOWNLOAD_DIR = './downloads/'

def download_send_udp_request(request_logs, tracker_ip, tracker_port, ip, port, msg, file_name, files):
    print('start download processing')

    client_socket = socket(AF_INET, SOCK_DGRAM)
    client_socket.bind((ip, int(port)))
    result_msg = send_udp_request(tracker_ip, tracker_port, client_socket, msg, ip, port)

    if not result_msg.startswith('error'):
        
        list_of_seeders, file_size = json.loads(result_msg)
                
        host_ip, host_port = random.sample(list_of_seeders, 1)[0]
        
        print('start download from ' + host_ip + ':' + str(host_port))
        
        client_socket = socket(AF_INET, SOCK_STREAM)
        try:
            client_socket.bind((ip, int(port)))
        except OSError:
            print('address busy')
            return
        client_socket.connect((host_ip, host_port))
        print('connect to server')
        client_socket.send(('download ' + file_name).encode())
        print('sent command to download')
        data, _ = client_socket.recvfrom(BUFFER_SIZE)
        data = data.decode()
        request_logs.append(data)
        print('finish downloading')

        if not data.startswith('error'):
            try:
                with open(DOWNLOAD_DIR + file_name, 'w') as f:
                    f.write(data)
                    f.close()
                client_socket.close()
                client_socket = socket(AF_INET, SOCK_DGRAM)
                send_udp_request_without_resp(client_socket, 'success ' + file_name + ' ' + ip + ':' + str(port) + ' ' + host_ip + ':' + str(host_port), tracker_ip, tracker_port)
                run_file_sharing_server(files, file_name, ip, port, tracker_ip, tracker_port)
            except:
                print('error writing_file')
                client_socket.close()
                client_socket = socket(AF_INET, SOCK_DGRAM)
                send_udp_request_without_resp(client_socket,
                                               'failed ' + file_name + ' ' + ip + ':' + str(port) + ' ' + host_ip + ':' + str(host_port),
                                               tracker_ip, tracker_port)
                exit(-1)
        else:
            client_socket.close()
            print('error fail_in_downloading')
            client_socket = socket(AF_INET, SOCK_DGRAM)
            send_udp_request(tracker_ip, tracker_port, client_socket, 'failed ' + file_name + ' ' + ip + ':' + str(port) + ' ' + host_ip + ':' + str(host_port), ip, port)
            exit(-1)
        client_socket.close()
    else:
        print('error failed_track_file')
        client_socket.close()
        client_socket = socket(AF_INET, SOCK_DGRAM)
        exit(-1)
