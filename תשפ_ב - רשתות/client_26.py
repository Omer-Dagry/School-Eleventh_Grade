"""
Author: Omer Dagry
Program name: 2.6
Description: client
             protocol: cccccccc|xxxx|d
                       c = command, pad with spaces until length 8
                       x = len data
                       d = data
Date: 20.10.2021
"""
import socket
import logging
import os

# logging
LOG_FORMAT = "%(levelname)s | %(asctime)s | %(processName)s | %(message)s"
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = LOG_DIR + "/client_26.log"

MAX_MSG_LENGTH = 1024
PORT = 8820
IP = "127.0.0.1"
KNOWN_RESPONDS = ["TIME", "NAME", "RAND", "EXIT", "ERROR"]


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


def build_message(request, msg=""):
    """
    builds a message by the protocol
    :param request: the request
    :param msg:
    :return: the message according to the protocol
    """
    return '%s|%s|%s' % (request.ljust(8), str(len(msg)).zfill(4), msg)


def handle_msg(msg):
    """
    handles the message from the server by the protocol
    :param msg: the message
    :return: command, data
    """
    data = ""
    for i in range(int(msg.split('|')[1]) + 13, 13, -1):
        data += msg[i]
    data = data[::-1]
    i = 0
    len_ = 14
    while i < len_:
        if msg[i] == " ":
            msg = msg[:i] + msg[i+1:]
            i -= 1
            len_ -= 1
        i += 1
    command = msg.split('|')[0]
    print(command, data)
    return command, data


def main():
    if not os.path.isdir(LOG_DIR):
        os.makedirs(LOG_DIR)
    logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)
    my_socket = create_socket()
    while True:
        request = input("Please enter request for server: [TIME / NAME / RAND / EXIT]\n")
        while len(request) != 4:
            print("Please enter exactly 4 chars.")
            request = input("Please enter request for server: [TIME / NAME / RAND / EXIT]\n")
        try:
            my_socket.send(build_message(request).encode())
            logging.info("    [Client]: " + build_message(request))
            command, data = handle_msg(my_socket.recv(MAX_MSG_LENGTH).decode())
            if command in KNOWN_RESPONDS:
                if data == "Ending connection...":
                    print("[Server]: " + command + ": " + data)
                    logging.debug("    [Server]: " + command + ":" + " Ending connection...")
                    my_socket.close()
                    exit()
                print("[Server]: " + command + ": " + data)
                logging.debug("    [Server]: " + command + ": " + data)
            else:
                print("ERROR unknown respond (%s)." % command)
                logging.warning("    ERROR unknown respond (%s)." % command)
        except ConnectionResetError:
            print("Lost connection with server.\nClosing the program.")
            logging.warning("    Lost connection with server.\\nClosing the program.")
            my_socket.close()
            exit()


if __name__ == '__main__':
    assert "check   |0002|ok" == build_message("check", "ok")
    assert "check", "ok" == handle_msg("check   |0002|ok")
    main()
