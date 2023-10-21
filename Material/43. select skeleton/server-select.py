"""
author; Nir Dweck
Date: 11/3/22
description: skeleton server which handles multiple clients by using select
"""
import sys
import socket
import select
import datetime
import logger
import commands
from User import User
from UsersMngr import UsersMngr


LOG_FILE = 'server.log'
USERS_FILE = 'conf/users.txt'
ADMIN_ROLE = 'admin'
USER_ROLE = 'user'
USER_ROLE_SEPARATOR = ','
USERS_LINE_SEPARATOR = '\n'
SERVER_IP = '0.0.0.0'
SERVER_PORT = 20003
LISTEN_SIZE = 5
READ_SIZE = 1024
ADMIN_SIGN = '!'
AT_SIGN = ':'


def send_chats_to_all(user, command, current_socket, open_client_sockets):
    """
    create messages to all the clients except the current socket
    :param user: the sending user
    :param command: the command object
    :param current_socket: the socket on which the message was received
    :param open_client_sockets: the list of open sockets
    :return: a list of tuples (socket, message) to be sent
    """
    return []


def send_waiting_massages(list_of_messages, wlist):
    """
    sends the list of messages to the required sockets if they are in wlist
    :param list_of_messages: a list of tuples of message and socket that
     needs to be sent
    :param wlist: the list of sockets ready to be sent on
    :return: None
    """
    for message in list_of_messages:
        client_socket, msg = message
        if client_socket in wlist:
            client_socket.send(msg.encode())
            list_of_messages.remove(message)


def logout(current_socket, open_client_sockets, mngr):
    """
    perform logout for the user holding the current socket, remove the user
     from the open sockets list and close the socket
    :param current_socket: the socket to perform the operation on
    :param open_client_sockets: the list of open sockets
    :param mngr: the user manager
    :return: None
    """
    pass


def main_loop(mngr):
    """
    the main server loop, waits for messages from clients and acts according
    :param mngr: the users manager instance
    :return: None, endless loop
    """
    server_socket = socket.socket()
    try:
        server_socket.bind((SERVER_IP, SERVER_PORT))
        server_socket.listen(LISTEN_SIZE)
        messages_to_send = []
        open_client_sockets = []
        send_sockets = []
        while True:
            rlist, wlist, xlist = select.select([server_socket]
                                                + open_client_sockets,
                                                send_sockets, open_client_sockets)
            print(datetime.datetime.now())
            # check for exception
            for current_socket in xlist:
                logger.log('handling exception socket')
                logout(current_socket, open_client_sockets, mngr)
            for current_socket in rlist:
                # check for new connection
                if current_socket is server_socket:
                    client_socket, client_address = current_socket.accept()
                    logger.log('received a new connection from '
                               + str(client_address[0]) + ':'
                               + str(client_address[1]))
                    open_client_sockets.append(client_socket)
                else:
                    # receive data
                    data = current_socket.recv(READ_SIZE).decode()
                    logger.log(data)
                    # check if connection was aborted
                    if data == "":
                        #socket was closed
                        logout(current_socket, open_client_sockets, mngr)
                    else:
                        # handle the received data
                        command = commands.parse(data)
                        if command.get_command() ==\
                                commands.LOGIN_SERVICE_COMMAND:
                            mngr.login_user(command.get_sender(),
                                            current_socket)
                        elif command.get_command() ==\
                                commands.CHAT_SERVICE_COMMAND:
                            messages_to_send.extend(send_chats_to_all(
                                mngr.get_user(current_socket), command,
                                current_socket, open_client_sockets))
            send_waiting_massages(messages_to_send, wlist)
            if len(messages_to_send) > 0:
                send_sockets = open_client_sockets
            else:
                send_sockets = []
    except socket.error as err:
        logger.log('received socket error - exiting, ' + str(err))
    finally:
        server_socket.close()


def main():
    """
    Add Documentation here
    """
    users = []
    mngr = UsersMngr(users)
    main_loop(mngr)


if __name__ == '__main__':
    logger.activate_log(LOG_FILE)
    main()