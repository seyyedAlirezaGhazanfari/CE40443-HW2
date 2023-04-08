from socket import *
from threading import Thread, Timer

BUFFER_SIZE = 1024
HEART_BEAT = 60
NUMBER_OF_CONNECTIONS = 5

def alive_report(ip, port, tracker_ip, tracker_port):
    msg = 'alive ' + ip + ':' + port
    client_socket = socket(AF_INET, SOCK_DGRAM)
    send_udp_request(tracker_ip, tracker_port, client_socket, msg, ip, port)

def heartbeat(my_ip, my_port, tracker_ip, tracker_port):
    Timer(HEART_BEAT, heartbeat, args=(my_ip, my_port, tracker_ip, tracker_port)).start()
    print('hi request for list of trackers')
    alive_report(my_ip, my_port, tracker_ip, tracker_port)

def send_udp_request(tracker_ip, tracker_port, client_socket, msg, ip, port):
    client_socket.sendto(msg.encode(), (tracker_ip, int(tracker_port)))
    result_msg, _ = client_socket.recvfrom(BUFFER_SIZE)
    client_socket.close()
    result_msg = result_msg.decode()
    return result_msg


def send_udp_request_without_resp(client_socket, msg, tracker_ip, tracker_port):
    client_socket.sendto(msg.encode(), (tracker_ip, int(tracker_port)))
    client_socket.close()

def upload_file(connection, request, cli_address, files):
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


def hanle_tcp_client(connection, client_address, files):
    while True:
        request, _ = connection.recvfrom(BUFFER_SIZE)
        request = request.decode()
        upload_file(connection, request, client_address, files)

def run_file_sharing_server(files, file_name, ip, port, tracker_ip, tracker_port):
    print("ready to share")
    new_thread_2 = Thread(target=heartbeat, args=(ip, port, tracker_ip, tracker_port))
    new_thread_2.start()  
    files.append(file_name)
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind((ip, int(port)))
    server_socket.listen(NUMBER_OF_CONNECTIONS)
    while True:
        connection, client_address = server_socket.accept()
        connection.setblocking(False)
        new_thread = Thread(target=hanle_tcp_client, args=(connection, client_address, files))
        new_thread.start()