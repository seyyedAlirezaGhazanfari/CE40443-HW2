from socket import *
from threading import Thread
from utils import BUFFER_SIZE, send_udp_request, run_file_sharing_server, heartbeat



def upload_send_udp_request(tracker_ip, tracker_port, ip, port, msg, file_name, files):
    client_socket = socket(AF_INET, SOCK_DGRAM)
    try:
        client_socket.bind((ip, int(port)))
    except OSError:
        print('busy address')
        return
    result_msg = send_udp_request(tracker_ip, tracker_port, client_socket, msg, ip, port)  
    if result_msg == 'OK':
        run_file_sharing_server(files, file_name, ip, port, tracker_ip, tracker_port)
    else:
        print('error registering_on_tracker')
        exit(-1)

