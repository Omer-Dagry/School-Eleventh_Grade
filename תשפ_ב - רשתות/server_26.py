"""
Author: Omer Dagry
Program name: 2.6
Description: server
             protocol: cccccccc|xxxx|d
                       c = command, pad with spaces until length 8
                       x = len data
                       d = data
Date: 20.10.2021
"""
import socket
import logging
import os
import datetime
import random

# logging
LOG_FORMAT = "%(levelname)s | %(asctime)s | %(processName)s | %(message)s"
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = LOG_DIR + "/server_26.log"

RECEIVE_SIZE = 1024
SERVER_PORT = 8820
SERVER_IP = "0.0.0.0"
SERVER_SOCKET_TIMEOUT = 30


def create_socket():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.settimeout(SERVER_SOCKET_TIMEOUT)
    try:
        server_socket.bind((SERVER_IP, SERVER_PORT))
    except socket.error as error:
        server_socket.close()
        logging.warning("       Socket error: " + str(error))
        print("Socket error: " + str(error) + "\nClosing server.")
        exit()
    server_socket.listen()
    logging.info("    Server is up and waiting for client.")
    print("Server is up and running")
    print("Waiting for client...")
    client_socket, client_address = server_socket.accept()
    logging.info("    Client connected. IP: " + str(client_address))
    print("Client connected")
    return server_socket, client_socket, client_address


def build_message(command, data):
    """
    builds a message by the protocol
    :param command: the command
    :param data: the data
    :return: msg according to the protocol
    """
    return '%s|%s|%s' % (command.ljust(8), str(len(data)).zfill(4), data)


def handle_msg(msg):
    """
    handles the message from the client
    :param msg: the message
    :return: the request
    """
    request = msg.split('|')[0]
    return request


def time():
    """
    creates a message for the client with the time
    :return: the message
    """
    t = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return build_message("TIME", t)


def name():
    """
    creates a message for the client with the name
    :return: the message
    """
    return build_message("NAME", "Joker")


def rand():
    """
    creates a message for the client with a random number
    :return: the same thing the client will get
    """
    return build_message("RAND", str(random.randint(1, 10)))


def exitt():
    """
    reates a message for the client with exit conformation
    :return: the message
    """
    return build_message("EXIT", "Ending connection...")


def unknown_request():
    """
    creates a message for the client that says that the request is unknown
    :return: the message
    """
    return build_message("ERROR", "Unknown request")


def send_log_print(msg, client_socket):
    """
    send 'msg' to 'client_socket'
    logs the action
    print the action
    :param msg: the message to send
    :param client_socket: the socket to send to
    """
    client_socket.send(msg.encode())
    logging.debug("    [Server]: '" + msg + "'")
    print("[Server]: '" + msg + "'")


def main():
    if not os.path.isdir(LOG_DIR):
        os.makedirs(LOG_DIR)
    logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)
    while True:
        try:
            server_socket, client_socket, client_address = create_socket()
        except socket.timeout:
            logging.warning("    Waited 30 seconds for client to connect, No connection made, Closing server.")
            print("Waited %d seconds for client to connect, No connection made, Closing server."
                  % SERVER_SOCKET_TIMEOUT)
            exit()
        while True:
            try:
                request = client_socket.recv(RECEIVE_SIZE).decode()
                logging.debug("    [Client]: '" + request + "'")
                print("[Client]: '" + request + "'")
                request = handle_msg(request)
                if request == "TIME    ":
                    msg = time()
                    send_log_print(msg, client_socket)
                elif request == "NAME    ":
                    msg = name()
                    send_log_print(msg, client_socket)
                elif request == "RAND    ":
                    msg = rand()
                    send_log_print(msg, client_socket)
                elif request == "EXIT    ":
                    msg = exitt()
                    send_log_print(msg, client_socket)
                    break
                else:
                    msg = unknown_request()
                    send_log_print(msg, client_socket)
            except ConnectionResetError:
                logging.warning("    Lost connection with client.")
                print("Lost connection with client.")
                break
        client_socket.close()
        server_socket.close()
        logging.info("    Client Disconnected.")
        print("Client Disconnected.")


if __name__ == '__main__':
    assert build_message("check", "ok") == "check   |0002|ok"
    assert name() == "NAME    |0005|Joker"
    assert 1 <= int(rand()[-1]) <= 10
    assert exitt() == "EXIT    |0020|Ending connection..."
    assert unknown_request() == "ERROR   |0015|Unknown request"
    main()
