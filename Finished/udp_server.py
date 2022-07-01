import socket

SERVER_IP = "0.0.0.0"
PORT = 8821
MAX_MSG_SIZE = 1024

print("Server up and running...")
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, PORT))
while True:
    (client_message, client_address) = server_socket.recvfrom(MAX_MSG_SIZE)
    data = client_message.decode()
    print("[Client]: " + data)
    server_socket.sendto(data.encode(), client_address)
    print("[Server]: " + data)
    if data == "EXIT":
        server_socket.sendto("Goodbye".encode(), client_address)
        break

server_socket.close()
