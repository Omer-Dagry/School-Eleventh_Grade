import socket
import time

SERVER_IP = "127.0.0.1"
PORT = 8821
MAX_MSG_SIZE = 1024

my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    msg = input("Please enter your msg: ")
    my_socket.sendto(msg.encode(), (SERVER_IP, PORT))
    tic = time.perf_counter()
    (response, remote_address) = my_socket.recvfrom(MAX_MSG_SIZE)
    toc = time.perf_counter()
    run_time = toc - tic
    print("Time send --> receive: %f" % run_time)
    print("[Server]: %s" % response.decode())
    if msg == "EXIT":
        break

my_socket.close()
