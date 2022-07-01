"""
Author: Omer Dagry
Program name: 2.7
Description: client
             protocol:
             1) command + ' ' until len 16 + # + len_data + ' ' until len 16
             2) data
Date: 24.10.2021
"""
import io
import socket
import logging
import os
from PIL import Image

# logging
LOG_FORMAT = "%(levelname)s | %(asctime)s | %(processName)s | %(message)s"
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = LOG_DIR + "/client_27.log"

RECEIVE_SIZE = 33
PORT = 8820
IP = "127.0.0.1"
KNOWN_RESPONDS = ["dir", "delete", "copy", "execute", "take_screenshot", "send_photo", "exit", "error"]


def create_socket():
    """
    creates a socket with the constants IP & PORT
    :return: the socket
    """
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        my_socket.connect((IP, PORT))
    except ConnectionRefusedError as error:
        my_socket.close()
        logging.warning("   Error: " + str(error))
        print("Error: couldn't connect to server.\nClosing program.")
        exit()
    logging.info("    Connected to server.")
    return my_socket


def recvv(server_socket, log=''):
    """
    protocol:    1) command_handled#len_data    2) data

    1) receives the first part of the protocol
    2) loops on the second part until it gets the len of data specified in
       the first part of the protocol, if on the first part the command is "send_photo"
       then it receives the data as type bytes else as type str

    :param server_socket: the socket of the client who is sending a message
    :param log: if you don't want to log all the data received because it is
                spam (photo bytes or all the files in a dir) pass through the log parameter
                "send_photo" or "dir" to log a dedicated msg for each case
    :return: the command & the data
    """
    len_data = RECEIVE_SIZE
    cmd_and_len_data = ""
    received_data_len = 0
    while len_data > 0:
        cmd_and_len_data += server_socket.recv(len_data).decode()
        received_data_len = len(cmd_and_len_data) - received_data_len
        len_data -= received_data_len
    logging.debug("    [Server]: '" + str(cmd_and_len_data) + "'")
    cmd = cmd_and_len_data.split('#')[0]
    len_data = cmd_and_len_data.split('#')[1]
    cmd = ''.join(cmd.split(' '))
    len_data = ''.join(len_data.split(' '))
    len_data = int(len_data)
    received_data_len = 0
    if cmd == "send_photo":
        data = bytes("".encode())
        while len_data > 0:
            data += server_socket.recv(len_data)
            received_data_len = len(data) - received_data_len
            len_data -= received_data_len
    else:
        data = ""
        while len_data > 0:
            data += server_socket.recv(len_data).decode()
            received_data_len = len(data) - received_data_len
            len_data -= received_data_len
    if log == "send_photo":
        logging.debug("    [Server]: " + cmd + ": " + "photo bytes")  # not logging the photo bytes (spam)
    elif log == "dir":
        logging.debug("    [Server]: " + cmd + ": " + "the files in specified dir")  # not logging the files (spam)
    else:
        logging.debug("    [Server]: " + cmd + ": " + data)
    return cmd, data


def send_log(data, cmd, server_socket):
    """
    sends cmd & len(data) to the server
    logs it
    sends data to the server
    logs it
    :param data: the data to send
    :param cmd: the request for the server
    :param server_socket: the socket to send to
    """
    server_socket.send((cmd.ljust(16) + '#' + str(len(data)).ljust(16)).encode())
    logging.debug("    [Client]: '" + cmd + '#' + str(len(data)) + "'")
    if len(data) != 0:
        server_socket.send(data.encode())
    logging.debug("    [Client]: '" + cmd + ": " + data + "'")


def requestt():
    """
    takes input from the user
    request to server and data if needed for the request
    :return: request, msg
    """
    r = input("Please enter request for server: [dir/delete/copy/execute/take_screenshot/send_photo/exit]\n")
    while len(r) > 16:
        r = input("Please enter request for server: [dir/delete/copy/execute/take_screenshot/send_photo/"
                  "exit]\nMAX CHARS IS 16!!!\n")
    if r == "dir":
        m = input("Please enter the path of the desired dir:\n")
    elif r == "delete":
        m = input("Please enter the path of the desired file to delete:\n")
    elif r == "copy":
        m = input("Please enter the path of the desired file to be copied:\n") + "|/|/|" + \
            input("Please enter the path of the new file:\n")
    elif r == "execute":
        m = input("Please enter the path of the desired program to be executed:\n")
    else:
        m = ""
    return r, m


def main():
    if not os.path.isdir(LOG_DIR):
        os.makedirs(LOG_DIR)
    logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)
    my_socket = create_socket()
    while True:
        request, msg = requestt()
        try:
            send_log(msg, request, my_socket)
            command, data = recvv(my_socket, request)
            if command in KNOWN_RESPONDS:
                if command == "exit":
                    my_socket.close()
                    print("[Server]: " + command + ": " + data)
                    exit()
                elif command == "send_photo":
                    image = Image.open(io.BytesIO(data))
                    image.show()
                else:
                    print("[Server]: " + command + ": " + data)
            else:
                print("ERROR unknown respond (%s)." % command)
                logging.warning("    ERROR unknown respond (%s)." % command)
        except ConnectionResetError:
            print("Lost connection with server.\nClosing the program.")
            logging.warning("    Lost connection with server.\\nClosing the program.")
            my_socket.close()
            exit()


if __name__ == '__main__':
    main()
