from socket import *
import time
import threading
import os
import math
import json

# Socket for UDP communication
peer_udp_sock = socket(AF_INET, SOCK_DGRAM)
peer_udp_send_sock = socket(AF_INET, SOCK_DGRAM)

# Socket for TCP communication
serverSocket = socket(AF_INET, SOCK_STREAM)

# List to store information about peers in the network
peer_list = []

# Broadcast address for UDP communication
broadcast_address = ('25.255.255.255', 12001)

# Dictionary to store local information about hosted chunks
local_dict = {}


# Function to convert data into chunks and save them as files
def data_to_chunk(data_name):
    try:
        content_name = data_name
        filename = content_name + '.png'
        c = os.path.getsize(filename)
        CHUNK_SIZE = math.ceil(math.ceil(c) / 5)

        index = 1
        with open(filename, 'rb') as infile:
            chunk = infile.read(int(CHUNK_SIZE))
            while chunk:
                chunkname = content_name + '_' + str(index) + 'chk'
                with open(chunkname, 'wb+') as chunk_file:
                    chunk_file.write(chunk)
                index += 1
                chunk = infile.read(int(CHUNK_SIZE))
    except:
        print('file not found')


# Function to get a list of all available chunks in the local directory
def all_available_chunks():
    chunks_list = []
    for root, dirs, files in os.walk(os.getcwd()):
        for name in files:
            if name.endswith("chk"):
                chunks_list.append(name)
    chunk_dictionary = {'chunks': chunks_list}
    return json.dumps(chunk_dictionary)


# Function to broadcast information about available chunks at regular intervals
def chunk_announcer(period, data_name):
    data_to_chunk(data_name)
    start_time = time.time()
    first_time = True
    while 1:
        current_time = time.time()
        if first_time:
            broadcast(all_available_chunks())
        if current_time - start_time > period:
            broadcast(all_available_chunks())
            start_time = time.time()
        first_time = False


# Function to receive data from peers over UDP
def RecvData(sock):
    while 1:
        data, address = sock.recvfrom(2048)
        local_dict = json.loads(data.decode("utf-8"))
        replika = False
        if len(peer_list) != 0:
            for peer in peer_list:
                if address[0] == peer[1][0]:
                    peer_list.pop(peer_list.index(peer))
                    peer_list.append((local_dict, address))
                    replika = True
            if not replika:
                peer_list.append((local_dict, address))
        else:
            peer_list.append((local_dict, address))
        if sub_flow:
            print(f'\nNew Submission: {peer_list[len(peer_list) - 1]}')


# Function to set up and run the UDP socket for peer communication
def runPeerSocket():
    port = 12001
    peer_udp_sock.bind(('', port))
    print('peer is online on IP, Port -> ' + str(peer_udp_sock.getsockname()))

    threading.Thread(target=RecvData, args=(peer_udp_sock,)).start()


# Function to handle uploading chunks over TCP
def chunk_Uploader():
    serverPort = 12000

    serverSocket.bind(('', serverPort))
    serverSocket.listen(5)
    while 1:
        connection_socket, addr = serverSocket.accept()
        wanted_file_name = connection_socket.recv(2048)
        if os.path.exists(wanted_file_name.decode("utf-8")):
            wanted_file = open(wanted_file_name.decode("utf-8"), 'rb')
            while 1:
                wanted_file_data = wanted_file.read(8000)
                connection_socket.send(wanted_file_data)
                if not wanted_file_data:
                    break
            wanted_file.close()
        else:
            connection_socket.send("ERROR: Wanted chunk could not be delivered. ".encode("utf_8"))
        connection_socket.close()


# Function to run the chunk downloader to retrieve chunks from other peers
def run_chunk_downloader(content_name, ownerIP):
    client_socket = socket(AF_INET, SOCK_STREAM)
    address = (ownerIP, 12000)
    print(f'Trying to connect to {address} to get {content_name}')
    client_socket.connect(address)

    client_socket.send(content_name.encode("utf-8"))
    incoming_file_data = client_socket.recv(4048)
    try:
        err_message = incoming_file_data.decode("utf_8")
        print(err_message)
    except:
        incoming_file = open(content_name, 'wb')
        while 1:
            incoming_file.write(incoming_file_data)
            incoming_file_data = client_socket.recv(4048)
            if len(incoming_file_data) <= 0:
                break
        print("file have been received successfully\n")
        incoming_file.close()

    client_socket.close()


# Function to download data from the network by requesting specific chunks
def download_data(content_name):
    req_chunks = []
    ip_chunk_list = []
    for x in range(5):
        req_chunks.append(content_name + '_' + str(x + 1) + 'chk')
    for peer in peer_list:
        chunk_list = peer[0].get('chunks')
        for chunks in chunk_list:
            for y in range(5):
                if chunks == req_chunks[y] and not os.path.exists(chunks):
                    ip_chunk_list.append((req_chunks[y], peer[1][0]))
                    break
    print(ip_chunk_list)
    if len(ip_chunk_list) == 0:
        print("Required file is not in the network. ")
    else:
        for ip_chunk in ip_chunk_list:
            run_chunk_downloader(ip_chunk[0], ip_chunk[1])


# Function to broadcast a message over UDP
def broadcast(message):
    peer_udp_send_sock.sendto(message.encode("utf-8"), broadcast_address)


# Function to stitch back the downloaded chunks into the original file
def stitch_back_file(content_name):
    chunk_names = [content_name + '_1chk', content_name + '_2chk', content_name + '_3chk', content_name + '_4chk', content_name + '_5chk']
    with open(content_name + '.png', 'wb') as outfile:
        for chunk in chunk_names:
            with open(chunk, 'rb') as infile:
                outfile.write(infile.read())
            infile.close()


# Flag to control the display of submission information
sub_flow = True

# Main loop for user interaction
index = 0
while 1:
    if index == 0:
        hosted_data = input('Enter the file to be hosted: ')
        threading.Thread(target=chunk_announcer, args=(60, hosted_data)).start()
        threading.Thread(target=chunk_Uploader, args=()).start()
        runPeerSocket()

    userInput = input('type /help for commands \n')
    if userInput == "/help":
        print("-/stopsubflow: stops the info messages when a new submissions occurs. \n"
              "-/keepsubflow: continues to print the info messages when a new submission occurs"
              "-/downloadfile: tries to download a specified file from network. \n"
              "-/
