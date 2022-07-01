"""
Author: Omer Dagry
Program name: 2.7
Description: server
             protocol:
             1) command_handled + ' ' until len 16 + # + len_data + ' ' until len 16
             2) data
Date: 24.10.2021
"""
import socket
import logging
import os
import glob
import shutil
import subprocess
import pyautogui

# logging
LOG_FORMAT = "%(levelname)s | %(asctime)s | %(processName)s | %(message)s"
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = LOG_DIR + "/server_27.log"

RECEIVE_SIZE = 33
SERVER_PORT = 8820
SERVER_IP = "0.0.0.0"
SERVER_SOCKET_TIMEOUT = 30


def create_socket(server_socket):
    """
    creates a socket with a client
    :return: server_socket & client_socket & client_address
    """
    server_socket.listen()
    logging.info("    Server is up and waiting for client.")
    print("Server is up and running")
    print("Waiting for client...")
    client_socket, client_address = server_socket.accept()
    logging.info("    Client connected. IP: " + str(client_address))
    print("Client connected")
    return server_socket, client_socket, client_address


def check():
    """
    checks some of the functions
    :return: if everything went well - True, else - False
    """
    os.makedirs(r"C:\check")
    a = open(r"C:\check\a.txt", 'w')
    b = open(r"C:\check\b.txt", 'w')
    c = open(r"C:\check\c.txt", 'w')
    d = open(r"C:\check\d.py", 'w')
    a.close()
    b.close()
    c.close()
    d.close()
    copy(r"C:\check\a.txt", r"C:\check\e.txt")
    take_screenshot(location=r"C:\check\screen.jpg")
    if dirr(r"C:\check") != "a.txt\nb.txt\nc.txt\nd.py\ne.txt\nscreen.jpg":
        return False
    delete(r"C:\check\a.txt")
    delete(r"C:\check\b.txt")
    delete(r"C:\check\c.txt")
    delete(r"C:\check\d.py")
    delete(r"C:\check\e.txt")
    delete(r"C:\check\screen.jpg")
    os.rmdir(r"C:\check")
    return True


def dirr(location):
    """
    returns all the files in "location" dir
    :param location: the location of the desired dir
    :return: all the files in "location" dir
    :rtype: str
    """
    if os.path.isdir(location):
        if location[-1] != "\\":
            location += "\\*.*"
        else:
            location += "*.*"
        files_list = glob.glob(location)
        for i in range(0, len(files_list)):
            files_list[i] = files_list[i].split("\\")[-1]
        return "\n".join(files_list)
    else:
        return "Dir doesn't exist"


def delete(file_location):
    """
    removes a file
    :param file_location: the location + name of the file to remove
    :return: "Removed" if removed, "File doesn't exists" if file doesn't exists
    :rtype: str
    """
    if os.path.isfile(file_location):
        os.remove(file_location)
        return "Removed"
    else:
        return "File doesn't exists"


def copy(file_location, copy_to):
    """
    copies a file to specified location
    :param file_location: the location + name of the file to copy
    :param copy_to: the location to copy the file + name of new file
    :return: "Copied" if copied, "File doesn't exists" if file doesn't exists
    :rtype: str
    """
    if os.path.isfile(file_location):
        shutil.copy(file_location, copy_to)
        return "Copied"
    else:
        return "File doesn't exists"


def execute(program_path):
    """
    executes a program
    :param program_path: the path of the program file
    :return: if worked - "Program executed"
             else - "File doesn't exist"
    :rtype: str
    """
    try:
        subprocess.call(program_path)
        return "Program executed"
    except FileNotFoundError as error:
        logging.debug(program_path + "    File doesn't exist " + str(error))
        return "File doesn't exist"


def take_screenshot(location="screen.jpg"):
    """
    takes a screen shot and saves it on the directory
    that this program is running from, under the name "screen.jpg"
    :param location: just for doing assert
    :return: "Screenshot taken"
    :rtype: str
    """
    image = pyautogui.screenshot()
    image.save(location)
    return "Screenshot taken"


def send_photo(client_socket):
    """
    sends the screen shot
    :param client_socket: the socket of the client who asked for the photo
    """
    if os.path.isfile("screen.jpg"):
        photo = open("screen.jpg", 'rb')
        photo_data = photo.read()
        photo.close()
        send_log_print(photo_data, "send_photo", client_socket, "photo bytes")  # not logging the photo bytes (spam)
    else:
        send_log_print("photo doesn't exists", "error", client_socket)


def exitt():
    """
    :return: a message to confirm exit
    :rtype: str
    """
    return "Ending connection..."


def unknown_request():
    """
    :return: a message to let the client know his request is unknown
    :rtype: str
    """
    return "Unknown request"


def recvv(client_socket):
    """
    protocol:    1) command#len_data    2) data

    1) receives the first part of the protocol
    2) loops on the second part until it gets the len of data specified in the first part of the protocol
    :param client_socket: the socket of the client who is sending a message
    :return: the command & the data
    :rtype: str
    """
    len_data = RECEIVE_SIZE
    cmd_and_len_data = ""
    received_data_len = 0
    while len_data > 0:
        cmd_and_len_data += client_socket.recv(len_data).decode()
        received_data_len = len(cmd_and_len_data) - received_data_len
        len_data -= received_data_len
    logging.debug("    [Client]: '" + str(cmd_and_len_data) + "'")
    print("[Client]: '" + str(cmd_and_len_data) + "'")
    cmd = cmd_and_len_data.split('#')[0]
    len_data = cmd_and_len_data.split('#')[1]
    cmd = ''.join(cmd.split(' '))
    len_data = ''.join(len_data.split(' '))
    len_data = int(len_data)
    data = ""
    if len_data != 0:
        received_data_len = 0
        while len_data > 0:
            data += client_socket.recv(len_data).decode()
            received_data_len = len(data) - received_data_len
            len_data -= received_data_len
    return cmd, data


def send_log_print(data, cmd, client_socket, log=''):
    """
    sends cmd & len(data) to the client
    logs & prints it
    sends data to the client
    logs & prints it
    :param data: the data to send
    :param cmd: the command handled
    :param client_socket: the socket to send to
    :param log: in case you don't want to log the data
    """
    client_socket.send((cmd.ljust(16) + '#' + str(len(data)).ljust(16)).encode())
    logging.debug("    [Server]: '" + cmd + '#' + str(len(data)) + "'")
    print("[Server]: '" + cmd.ljust(16) + '#' + str(len(data)).ljust(16) + "'")
    if type(data) == str:
        client_socket.send(data.encode())
    elif type(data) == bytes:
        client_socket.send(data)
    else:
        client_socket.send(str(data))
    if log != '':
        logging.debug("    [Server]: '" + cmd + ": " + log + "'")
        print("[Server]: '" + log + "'")
    else:
        logging.debug("    [Server]: '" + cmd + ": " + str(data) + "'")
        print("[Server]: '" + str(data) + "'")


def main():
    if not os.path.isdir(LOG_DIR):
        os.makedirs(LOG_DIR)
    logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.settimeout(SERVER_SOCKET_TIMEOUT)
    try:
        server_socket.bind((SERVER_IP, SERVER_PORT))
    except socket.error as error:
        server_socket.close()
        logging.warning("       Socket error: " + str(error))
        print("Socket error: " + str(error) + "\nClosing server.")
        exit()
    while True:
        try:
            server_socket, client_socket, client_address = create_socket(server_socket)
        except socket.timeout:
            logging.warning("    Waited 30 seconds for client to connect, No connection made, Closing server.")
            print("Waited %d seconds for client to connect, No connection made, Closing server."
                  % SERVER_SOCKET_TIMEOUT)
            exit()
        while True:
            try:
                request, data = recvv(client_socket)
                logging.debug("    [Client]: '" + data + "'")
                print("[Client]: '" + data + "'")
                if request == "dir":
                    data = dirr(data)
                    # not logging the files in the dir (spam)
                    send_log_print(data, request, client_socket, "the files in specified dir")
                elif request == "delete":
                    data = delete(data)
                    send_log_print(data, request, client_socket)
                elif request == "copy":
                    copy_from = data.split("|/|/|")[0]
                    copy_to = data.split("|/|/|")[1]
                    data = copy(copy_from, copy_to)
                    send_log_print(data, request, client_socket)
                elif request == "execute":
                    data = execute(data)
                    send_log_print(data, request, client_socket)
                elif request == "take_screenshot":
                    data = take_screenshot()
                    send_log_print(data, request, client_socket)
                elif request == "send_photo":
                    send_photo(client_socket)
                elif request == "exit":
                    data = exitt()
                    send_log_print(data, request, client_socket)
                    break
                else:
                    data = unknown_request()
                    send_log_print(data, "error", client_socket)
            except ConnectionResetError:
                logging.warning("    Lost connection with client.")
                print("Lost connection with client.")
                break
        client_socket.close()
        logging.info("    Client Disconnected.")
        print("Client Disconnected.")


if __name__ == '__main__':
    assert check()
    main()
