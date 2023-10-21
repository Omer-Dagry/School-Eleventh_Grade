import socket
import logging
import os

# logging
LOG_FORMAT = "%(levelname)s | %(asctime)s | %(processName)s | %(message)s"
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = LOG_DIR + "/exam.log"

IP = "172.16.9.156"
PORT = 8080
SERVER_IP = "0.0.0.0"
MESSAGE_WITH_ID = "GET /randevus?id=215200908 HTTP/1.1\r\nAuthorization: darth-vader\r\n\r\n"


def create_client_socket(port):
    """
    creates a socket with the constants IP & PORT
    :return: the socket
    """
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        my_socket.connect((IP, port))
    except ConnectionRefusedError as error:
        my_socket.close()
        logging.warning("   Error: " + str(error))
        print("Error: couldn't connect to server.\nClosing program.")
        exit()
    logging.info("    Connected to server.")
    return my_socket


def create_server_socket(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((SERVER_IP, port))
    except socket.error as error:
        server_socket.close()
        logging.warning("       Socket error: " + str(error))
        print("Socket error: " + str(error) + "\nClosing server.")
        print(error)
        exit()
    server_socket.listen()
    logging.info("    Server is up and waiting for client.")
    print("Server is up and running")
    print("Waiting for client...")
    client_socket, client_address = server_socket.accept()
    logging.info("    Client connected. IP: " + str(client_address))
    print("Client connected")
    return server_socket, client_socket, client_address


def main():
    if not os.path.isdir(LOG_DIR):
        os.makedirs(LOG_DIR)
    logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)
    logging.info("I am the client")
    my_socket = create_client_socket(PORT)
    try:
        my_socket.send(MESSAGE_WITH_ID.encode())
        logging.info("    [Client]: " + MESSAGE_WITH_ID)
        response = ""
        while True:
            response += my_socket.recv(1).decode()
            if "\r\n\r\n" in response:
                break
            if response == "":
                my_socket.close()
                break
        logging.debug("    [Server]: " + response)
        response_list = response.split("\r\n")
        content_length = int(response_list[2][-1])
        data = ""
        while len(data) != content_length:
            data += my_socket.recv(1).decode()
        logging.debug("    [Server]: " + data)
        logging.info("I am the server")
        server_port = int(data)
        server_socket, client_socket, client_address = create_server_socket(server_port)
        data2 = ""
        while len(data2) < 156:
            data2 += client_socket.recv(1).decode()
        logging.debug("    [Client]: " + data2)
        print(data2)
    except socket.error as error:
        print(error)
    finally:
        my_socket.close()
        client_socket.close()
        server_socket.close()


if __name__ == '__main__':
    main()
