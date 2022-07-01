"""
Author: Omer Dagry
Program name: Chats
Description: Server
Date: 06.03.2022

Protocol:
------------------------------------------- Regular Message ------------------------------------------------------------
sends data len with padding and username with padding
for example if len is 82 it will send '82              ############Omer'
after this it sends the data with separation between fields & fields description & number of fields, for example:
2#@?#can_chat#@?#msg#@?#True#@?#
-------------------------------------------- Sync Message --------------------------------------------------------------
"number_of_files.ljust(16) + file_name.ljust(16) + file_len.ljust(16) + file_data"
Example:
"2               Omer2.txt                               41              connected_users.txt"
"0               Omer2: #@?!?##*#@?!#Omer2: hdfghdfgh#@?!#""
"""
import logging
import os
import select
import shutil
import socket
from datetime import datetime

# logging
LOG_FORMAT = "%(levelname)s | %(asctime)s | %(processName)s | %(message)s"
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = LOG_DIR + "/Chats-Server.log"


# constants
SERVER_PORT = 8822
SERVER_IP = "0.0.0.0"
R_SIZE = 16
TAKEN_USER_NAMES = ["Home", "connected_users", "last_seen"]

# globals
open_client_sockets = []
messages_to_send = []


class UploadFileFailed(Exception):
    """ Raises when the data received from a socket is '' (in the upload_file func) """


def start_server(server_socket):
    """
    initialize server socket
    :param server_socket:
    :type server_socket: socket.socket
    """
    try:
        server_socket.bind((SERVER_IP, SERVER_PORT))
        server_socket.listen()
        print("Listening for clients...")
        logging.info("Listening for clients...")
    except Exception as err:
        print(str(err))
        logging.warning(str(err) + " (start server)")
        server_socket.close()


def receive(current_socket):
    """
    receives one message (data len & username & data)
    :param current_socket: the socket of the client to receive a message from
    :type current_socket: socket.socket
    :return: tuple of the data and a boolean
    :rtype: tuple (str, bool)
    """
    try:
        # receive data len
        stop = False
        data = ""
        left_to_receive = R_SIZE
        while left_to_receive > 0:
            r = current_socket.recv(left_to_receive).decode()
            data += r
            left_to_receive = R_SIZE - len(data)
            if r == "":
                open_client_sockets.remove(current_socket)
                current_socket.close()
                stop = True
                break
        # receive username
        if not stop:
            user_name = ""
            left_to_receive = R_SIZE
            while left_to_receive > 0:
                r = current_socket.recv(left_to_receive).decode()
                user_name += r
                left_to_receive = R_SIZE - len(user_name)
                if r == "":
                    open_client_sockets.remove(current_socket)
                    current_socket.close()
                    stop = True
                    break
            if not stop:
                while '#' in user_name:
                    i = user_name.index('#')
                    user_name = user_name[:i] + user_name[i + 1:]
                data_len = ""
                for char in data:
                    if char.isnumeric():
                        data_len += char
                if len(data_len) > 0:
                    data_len = int(data_len)
                    left = data_len
                    data = ""
                    # receive data
                    while left > 0:
                        r = current_socket.recv(left).decode()
                        data += r
                        left = data_len - len(data)
                        if r == "":
                            open_client_sockets.remove(current_socket)
                            current_socket.close()
                            stop = True
                            break
                    if not stop:
                        char_val = data.split(',')
                        data = ""
                        for val in char_val:
                            if val.isnumeric():
                                data += chr(int(val))
                        return data, stop
                    else:
                        return '', stop
                else:
                    return '', stop
            else:
                return '', stop
        else:
            return '', stop
    except Exception as err:
        print(str(err), "(receive)")
        logging.warning(str(err) + " (receive)")
        print("Connection With: %s:%s Is Over" % (current_socket.getpeername()[0],
                                                  current_socket.getpeername()[1]))
        logging.warning("Connection With: %s:%s Is Over" % (current_socket.getpeername()[0],
                                                            current_socket.getpeername()[1]))
        if current_socket in open_client_sockets:
            open_client_sockets.remove(current_socket)
        current_socket.close()
        return '', True


def disassemble_protocol(data):
    """
    disassembles the received data according to the protocol
    :param data: the data to disassemble according to the protocol
    :type data: str
    :return: the command, list of fields, list of the data of fields
    :rtype: tuple (str, list of strs, list of strs)
    """
    data_list = data.split('#@?#')
    cmd = data_list[0]
    del data_list[0]
    number_of_fields = int(data_list[0])
    fields = [data_list[i] for i in range(1, number_of_fields + 1)]
    data_of_fields = [data_list[i] for i in range(number_of_fields + 1, len(data_list))]
    return cmd, fields, data_of_fields


def assemble_protocol(number_of_fields, fields, data_of_fields):
    """
    assembles a message according to the protocol
    :param number_of_fields: the number of fields in the message
    :param fields: the title of each field
    :param data_of_fields: the data of each field
    :type number_of_fields: int or str
    :type fields: list of strs
    :type data_of_fields: list of strs
    :return: the message according to the protocol
    :rtype: str
    """
    data_to_send = str(number_of_fields) + "#@?#"
    for field in fields:
        data_to_send += field + "#@?#"
    for data in data_of_fields:
        data_to_send += data + "#@?#"
    data_to_send = data_to_send[:-4]
    return data_to_send


def read_file(file_location, mode='r'):
    """
    opens the file at file_location reads the data closes the file
    :param file_location: the location of the file you want to read from
    :param mode: open file with a different mode, only read modes!!
    :return: the data in the file
    """
    if 'w' in mode:
        return None
    try:
        if 'b' in mode:
            file = open(file_location, mode)
        else:
            file = open(file_location, mode, encoding='utf-8')
        data = file.read()
        file.close()
        return data
    except FileNotFoundError:
        print("The file '%s' doesn't exists (read %s)" % (file_location, mode))
        logging.warning("The file '%s' doesn't exists (read %s)" % (file_location, mode))
        return None


def write_file(file_location, data, mode='w'):
    """
    opens the file at file_location adds the data to is and closes the file
    :param file_location: the location of the file you want to read from
    :param data: the data you want to add to the file
    :param mode: open file with a different mode, only write modes!!
    :return: True if nothing failed
    """
    if 'r' in mode:
        return None
    try:
        if 'b' in mode:
            file = open(file_location, mode)
            file.write(read_file(file_location, 'rb') + data)
        else:
            file = open(file_location, mode, encoding='utf-8')
            file.write(read_file(file_location) + data)
        file.close()
        return True
    except FileNotFoundError:
        print("The file '%s' doesn't exists (write %s)" % (file_location, mode))
        logging.warning("The file '%s' doesn't exists (write %s)" % (file_location, mode))
        return None


def log_in(user_name, password, client_socket):
    """
    if the handled cmd is login then this function checks if the username and password match
    if they do it return a matching message and adds the user to the connected_users.txt file
    :param user_name: the username
    :param password: the password
    :param client_socket: the socket of the client that requested to login
    :type user_name: str
    :type password: str
    :type client_socket: socket.socket
    :return: tuple of 'True' / 'False', the username, a matching message
    :rtype: tuple (str, str, str)
    """
    connected = read_file("connected_users.txt")
    data = read_file("users.txt")
    user_password = data.split('\n')
    users = [user_password[i] for i in range(0, len(user_password), 2)]
    passwords = [user_password[i] for i in range(1, len(user_password), 2)]
    if "#@!#" + user_name + "=" in connected:
        return 'False', user_name, 'User Already Connected'
    if user_name in users:
        if password == passwords[users.index(user_name)]:
            # add user to connected_users.txt file
            connected += "#@!#" + user_name + "=" + str(client_socket.getpeername()[0]) + ":" + \
                str(client_socket.getpeername()[1]) + "#@!#"
            write_file("connected_users.txt", connected)
            # update all the users that has a chat with the user
            known_users_to_the_user = os.listdir("chats\\" + user_name + "\\")  # get all the files in the user library
            for user in users:
                if user != "" and user + ".txt" in known_users_to_the_user:
                    new_data = read_file("chats\\" + user + "\\" + "new_data.txt")
                    write_file("chats\\" + user + "\\" + "new_data.txt", new_data + "connected_users.txt\n")
            # remove user from last_seen.txt file
            last_seen = read_file('last_seen.txt')
            if "#@!#" + user_name + " = " in last_seen:
                last_seen = last_seen.split('#@!#')
                for user in last_seen:
                    if user.startswith(user_name + " = "):
                        del last_seen[last_seen.index(user)]
                        break
                write_file('last_seen.txt', '#@!#'.join(last_seen))
            else:
                write_file('last_seen.txt', last_seen)
            logging.info(user_name + " Logged in")
            return 'True', user_name, "Logged In Successfully"
        else:
            logging.info(user_name + " Wrong Password")
            return 'False', user_name, "User Name Or Password Is Incorrect"
    else:
        logging.info(user_name + " User Name Doesn't Exists")
        return 'False', user_name, "User Name Or Password Is Incorrect"


def sign_up(user_name, password):
    """
    if the handled cmd is signup then this function checks if the username is available
    if it does it return a matching message and adds the user and password to the users.txt file
    :param user_name: the username
    :param password: the password
    :type user_name: str
    :type password: str
    :return: tuple of 'True' / 'False', the username, a matching message
    :rtype: tuple (str, str, str)
    """
    if user_name in TAKEN_USER_NAMES:
        return 'False', user_name, "This User Name Is Taken"
    data = read_file("users.txt")
    user_password = data.split('\n')
    users = [user_password[i] for i in range(0, len(user_password), 2)]
    for user in users:
        users[users.index(user)] = user.lower()
    if user_name.lower() in users:
        logging.info(user_name + " Signed Failed User Is Taken")
        return 'False', user_name, "This User Name Is Taken"
    ok = write_file("users.txt", data + user_name + "\n" + password + "\n")
    if ok:
        user_chats_dir = 'chats\\' + user_name
        os.mkdir(user_chats_dir)
        ok = write_file(user_chats_dir + "\\" + "new_data.txt", "")
        if ok:
            logging.info(user_name + " Signed Up")
            return 'True', user_name, "Signed Up Successfully"
        else:
            shutil.rmtree(user_chats_dir)
            logging.debug(user_name + " Error With Signing Up")
            return 'False', user_name, "Something Went wrong"
    else:
        logging.debug(user_name + " Error With Signing Up")
        return 'False', user_name, "Something Went wrong"


def sync(user_name, first_time, current_socket):
    """
    if the handled cmd is sync then this function will read the new_data.txt file and send the
    client all the files that are listed in the new_data.txt file and will empty the new_data.txt file
    :param user_name: the username
    :param first_time: if it is the first sync it will send everything even if it is not in the new_data.txt file
    :param current_socket: the socket of the client
    :type user_name: str
    :type first_time: str ('True' or 'False', can't send boolean value through the socket so str of true and false)
    :type current_socket: socket.socket
    """
    global messages_to_send
    data = read_file("users.txt")
    user_password = data.split('\n')
    users = [user_password[i] for i in range(0, len(user_password), 2)]
    if user_name not in users:
        return
    user_chats_dir = 'chats\\' + user_name
    if (read_file(user_chats_dir + "\\" + "new_data.txt") != "") or (first_time == 'True'):
        if first_time == 'True':
            chats = os.listdir(user_chats_dir + "\\")
        else:
            chats = read_file(user_chats_dir + "\\" + "new_data.txt")
            chats = chats.split("\n")
        i = 0
        while i < len(chats):  # remove unwanted files
            if "file_count_" in chats[i]:
                del chats[i]
                i -= 1
            i += 1
        for file_name in chats:  # remove duplicates
            while chats.count(file_name) > 1:
                chats.remove(file_name)
        if "" in chats:
            chats.remove("")
        if "new_data.txt" in chats:
            chats.remove("new_data.txt")
        while "connected_users.txt" in chats:
            chats.remove("connected_users.txt")
        chats_data = []
        i = 0
        while i < len(chats):  # get each file data
            chats_data.append(read_file(user_chats_dir + "\\" + chats[i], mode='rb'))
            i += 1
        write_file(user_chats_dir + "\\" + "new_data.txt", "")  # reset new_data file
        # add connected_users.txt file
        chats.append("connected_users.txt")
        # get the connected users and handle the data
        connected_users = read_file("connected_users.txt").split("#@!#")
        while "" in connected_users:  # remove empty lines
            connected_users.remove("")
        known_users_to_the_user = os.listdir(user_chats_dir + "\\")  # get all the files in the user library
        for file in known_users_to_the_user:  # remove all the files that doesn't end with ".txt"
            if not file.endswith(".txt"):
                known_users_to_the_user.remove(file)
        i = 0
        while i < len(connected_users):  # remove all the users that the user doesn't know (for security reasons)
            user = connected_users[i]
            if user.split('=')[0] + ".txt" not in known_users_to_the_user:
                connected_users.remove(user)
            else:
                connected_users[i] = user.split('=')[0]
                i += 1
        chats_data.append("#@!#".join(connected_users).encode())  # add the data to all the files that need to be sent
        # add last_seen.txt file
        chats.append("last_seen.txt")
        # get the last seen file data and handle the data
        last_seen = read_file("last_seen.txt").split("#@!#")
        i = 0
        while i < len(last_seen):  # remove all the users that the user doesn't know (for security reasons)
            user = last_seen[i]
            if user.split(' = ')[0] + ".txt" not in known_users_to_the_user:
                last_seen.remove(user)
            else:
                i += 1
        chats_data.append("#@!#".join(last_seen).encode())  # add the data to all the files that need to be sent
        data_to_send = ""
        messages_to_send.append((current_socket, str(len(chats)).ljust(16).encode()))
        for chat in chats:
            data_to_send += chat.ljust(40) + str(len(chats_data[chats.index(chat)])).ljust(16)
        messages_to_send.append((current_socket, data_to_send.encode()))
        for chat_data in chats_data:
            messages_to_send.append((current_socket, chat_data))
    else:
        messages_to_send.append((current_socket, '1'.ljust(16).encode()))
        messages_to_send.append((current_socket, ("No Changes".ljust(40) + "10".ljust(16)).encode()))
        messages_to_send.append((current_socket, b"No Changes"))


def chat_with(user_name, other_username):
    """
    if the handled cmd is chat_with then this function checks if the requested username to chat with exists
    if it does it creates a new txt file for both the user and the other user for the chat and
    updates the new_data.txt file
    :param user_name: the username
    :param other_username: the name of the desired username to chat with
    :type user_name: str
    :type other_username: str
    :return: 'True' or 'False'
    :rtype: str
    """
    data = read_file("users.txt")
    user_password = data.split('\n')
    users = [user_password[i] for i in range(0, len(user_password), 2)]
    if other_username == "" or user_name == "":
        return 'False', ''
    if other_username == user_name:
        return 'False', "You Can't Start A Chat With Yourself"
    if other_username in users and user_name in users:
        if not os.path.isfile('chats\\' + user_name + "\\" + other_username + ".txt"):
            ok = write_file('chats\\' + user_name + "\\" + other_username + ".txt", "")
            ok2 = write_file('chats\\' + other_username + "\\" + user_name + ".txt", "")
            new_data = read_file('chats\\' + user_name + "\\" + "new_data.txt")
            write_file('chats\\' + user_name + "\\" + "new_data.txt", new_data + other_username + ".txt\n")
            new_data = read_file('chats\\' + other_username + "\\" + "new_data.txt")
            write_file('chats\\' + other_username + "\\" + "new_data.txt", new_data + user_name + ".txt\n")
            if not (ok and ok2):
                return 'False', 'Error'
            return 'True', ''
        else:
            return 'False', "Chat Already Exists"
    else:
        return 'False', "Username Doesn't Exists"


def remove_unread_messages_notification(user_name, other_username):
    """
    removes the notification of 'unread messages' from the user_name chat with other_username
    :param user_name: the user to remove the notification from
    :param other_username: the username of the chat that the notification is in
    :type user_name: str
    :type other_username: str
    """
    if other_username != "Home":
        data = read_file('chats\\' + user_name + "\\" + other_username + ".txt")
        if "#@?!?##*" in data:
            data = data.split("#@?!#")
            while "" in data:
                data.remove("")
            if other_username + ": " + "#@?!?##*" in data:
                data.remove(other_username + ": " + "#@?!?##*")
                new_data = read_file('chats\\' + user_name + "\\" + "new_data.txt")
                write_file('chats\\' + user_name + "\\" + "new_data.txt", new_data + other_username + ".txt\n")
        if type(data) == list:
            data = "#@?!#".join(data) + "#@?!#"
        write_file('chats\\' + user_name + "\\" + other_username + ".txt", data)


def send_message(user_name, other_username, msg):
    """
    if the handled cmd is send_msg then this function will check if there is a chat for the two usernames
    if there is it will send the message and update the new_data.txt file
    it also removes the 'unread messages' notification if there is one
    :param user_name: the username
    :param other_username: the username of the person the text is for
    :param msg: the msg
    :type user_name: str
    :type other_username: str
    :type msg: str
    :return: 'True' or 'False'
    :rtype: str
    """
    if os.path.isfile('chats\\' + user_name + "\\" + other_username + ".txt") and \
            os.path.isfile('chats\\' + other_username + "\\" + user_name + ".txt"):
        # new_data file of username
        new_data = read_file('chats\\' + user_name + "\\" + "new_data.txt")
        write_file('chats\\' + user_name + "\\" + "new_data.txt", new_data + other_username + ".txt\n")
        # new_data file of other_username
        new_data = read_file('chats\\' + other_username + "\\" + "new_data.txt")
        write_file('chats\\' + other_username + "\\" + "new_data.txt", new_data + user_name + ".txt\n")
        # call read func because if username is sending a message to
        # other_username that means he read the chat
        read(user_name, other_username)
        # remove unread messages notification because the user sent a
        # message in the chat so that means he read the new messages
        remove_unread_messages_notification(user_name, other_username)
        # insert the message for username
        data = read_file('chats\\' + user_name + "\\" + other_username + ".txt")
        write_file('chats\\' + user_name + "\\" + other_username + ".txt", data + user_name + ": " + msg + "#@?!#")
        # insert the message for other_username + unread messages notification if needed
        data = read_file('chats\\' + other_username + "\\" + user_name + ".txt")
        if "#@?!?##*" not in data and other_username + " = " + user_name not in read_file('where.txt'):
            write_file('chats\\' + other_username + "\\" + user_name + ".txt", data + user_name + ": " + "#@?!?##*" +
                       "#@?!#" + user_name + ": " + msg + "#@?!#")
        else:
            write_file('chats\\' + other_username + "\\" + user_name + ".txt", data + user_name + ": " + msg + "#@?!#")
        return 'True'
    else:
        return 'False'


def read(user_name, other_username):
    """
    if the handled cmd is read then this function will add the date and time to the messages that other_username
    sent to user_name and remove the 'unread messages' notification
    this function also writes to a file the chat that the user is in, in order to know if a new messages is sent
    to him whether the server should add also the "unread messages" notification or not (if the user is in the chat
    it won't add the notification)
    :param user_name: the username of the user that read the message
    :param other_username: the username of the user that sent the message
    :type user_name: str
    :type other_username: str
    :return: True or False
    :rtype: bool
    """
    data = read_file("users.txt")
    user_password = data.split('\n')
    users = [user_password[i] for i in range(0, len(user_password), 2)]
    if user_name in users and other_username == "Home":
        # write to a file the chat the user is in
        data = read_file('where.txt')
        if user_name + " = " in data:
            data = data.split("\n")
            for i in range(0, len(data)):
                if user_name + " = " in data[i]:
                    if data[i] != user_name + " = " + other_username:
                        if data[i].split(" = ")[-1] in users:
                            remove_unread_messages_notification(data[i].split(" = ")[0], data[i].split(" = ")[1])
                        data[i] = user_name + " = " + other_username
                    break
            data = "\n".join(data)
        write_file('where.txt', data)
        return True
    if user_name in users and other_username in users:
        # write to a file the chat the user is in
        data = read_file('where.txt')
        if user_name + " = " in data:
            data = data.split("\n")
            for i in range(0, len(data)):
                if user_name + " = " in data[i]:
                    if data[i] != user_name + " = " + other_username:
                        if data[i].split(" = ")[1] != "Home":
                            remove_unread_messages_notification(data[i].split(" = ")[0], data[i].split(" = ")[1])
                        data[i] = user_name + " = " + other_username
                    break
            data = "\n".join(data)
        else:
            data += user_name + " = " + other_username + "\n"
        write_file('where.txt', data)
        # add date and time
        data = read_file('chats\\' + other_username + "\\" + user_name + ".txt")
        data = data.split("#@?!#")
        data_to_write = ""
        while "" in data:
            data.remove("")
        for line in data:
            if line.startswith(other_username + ": ") and "#@!#" not in line and \
                    "#@##@!?#This Message Was Deleted." not in line and "#@##@!?#Don'tDisplay" not in line:
                date_and_time = datetime.now().strftime("%m/%d/%Y, %H:%M")
                data_to_write += line + "#@!#(seen at %s)#@?!#" % date_and_time
                new_data = read_file('chats\\' + other_username + "\\" + "new_data.txt")
                write_file('chats\\' + other_username + "\\" + "new_data.txt", new_data + user_name + ".txt\n")
            else:
                data_to_write += line + "#@?!#"
        return write_file('chats\\' + other_username + "\\" + user_name + ".txt", data_to_write)
    else:
        return False


def upload_file(user_name, other_username, file_size, file_ends_with, current_socket):
    """
    if the handled cmd is upload_file then this function will receive the file data and set a name for it and then
    write it to the client folder and the other user folder and update the new_data.txt for both users
    it also removes the 'unread messages' notification if there is one
    :param user_name: the username of the user that sent the file
    :param other_username: the username of the user that the file is sent to
    :param file_size: the size of the file in bytes (from the message)
    :param file_ends_with: the file extension
    :param current_socket: the socket of the client that sent the file
    :type user_name: str
    :type other_username: str
    :type file_size: int or str (numbers)
    :type file_ends_with: str
    :type current_socket: socket.socket
    :return: True if everything is ok else False
    :rtype: bool
    """
    data = read_file("users.txt")
    user_password = data.split('\n')
    users = [user_password[i] for i in range(0, len(user_password), 2)]
    if user_name in users and other_username in users:
        # get the data of the file
        file_size = int(file_size)
        left = file_size
        file_data = b''
        try:
            while left > 0:
                r = current_socket.recv(left)
                file_data += r
                left = file_size - len(file_data)
                if r == b'':
                    open_client_sockets.remove(current_socket)
                    current_socket.close()
                    raise UploadFileFailed  # in order to stop receiving the file
        except Exception as err:
            print(str(err), "(upload_file)")
            logging.warning(str(err), "(upload_file)")
            return False
        # generate the file name
        ok = True
        if os.path.isfile('chats\\' + user_name + "\\" + "file_count_" + other_username + ".txt"):
            file_name_user = read_file('chats\\' + user_name + "\\" + "file_count_" + other_username + ".txt")
        else:
            ok = write_file('chats\\' + user_name + "\\" + "file_count_" + other_username + ".txt", "0")
            file_name_user = read_file('chats\\' + user_name + "\\" + "file_count_" + other_username + ".txt")
        ok2 = True
        if os.path.isfile('chats\\' + other_username + "\\" + "file_count_" + user_name + ".txt"):
            file_name_other = read_file('chats\\' + other_username + "\\" + "file_count_" + user_name + ".txt")
        else:
            ok2 = write_file('chats\\' + other_username + "\\" + "file_count_" + user_name + ".txt", "0")
            file_name_other = read_file('chats\\' + other_username + "\\" + "file_count_" + user_name + ".txt")
        # add 1 to the file_name counter for both users
        ok3 = write_file('chats\\' + user_name + "\\" + "file_count_" + other_username + ".txt",
                         str(int(file_name_user) + 1))
        ok4 = write_file('chats\\' + other_username + "\\" + "file_count_" + user_name + ".txt",
                         str(int(file_name_other) + 1))
        # add to the text file of both users
        data = read_file('chats\\' + user_name + "\\" + other_username + ".txt")
        data += user_name + ": #@??##" + other_username + "_" + file_name_user + file_ends_with + "#@?!#"
        ok5 = write_file('chats\\' + user_name + "\\" + other_username + ".txt", data)
        data = read_file('chats\\' + other_username + "\\" + user_name + ".txt")
        if "#@?!?##*" not in data and other_username + " = " + user_name not in read_file('where.txt'):
            ok6 = write_file('chats\\' + other_username + "\\" + user_name + ".txt", data + user_name + ": " +
                             "#@?!?##*" + "#@?!#" + user_name + ": #@??##" + user_name + "_" + file_name_other +
                             file_ends_with + "#@?!#")
        else:
            ok6 = write_file('chats\\' + other_username + "\\" + user_name + ".txt", data + user_name + ": #@??##" +
                             user_name + "_" + file_name_other + file_ends_with + "#@?!#")
        # add the new file and the text file to the new_data file for both users
        new_data = read_file('chats\\' + other_username + "\\" + "new_data.txt")
        ok7 = write_file('chats\\' + other_username + "\\" + "new_data.txt", new_data + user_name + ".txt\n" +
                         user_name + "_" + file_name_other + file_ends_with)
        new_data = read_file('chats\\' + user_name + "\\" + "new_data.txt")
        ok8 = write_file('chats\\' + user_name + "\\" + "new_data.txt", new_data + other_username + ".txt\n" +
                         other_username + "_" + file_name_user + file_ends_with + "\n")
        # write the file to both of the users folders
        ok9 = write_file('chats\\' + other_username + "\\" + user_name + "_" + file_name_other + file_ends_with,
                         file_data, mode="wb")
        ok10 = write_file('chats\\' + user_name + "\\" + other_username + "_" + file_name_user + file_ends_with,
                          file_data, mode="wb") and ok and ok2 and ok3 and ok4 and ok5 and ok6 and ok7 and ok8 and ok9
        remove_unread_messages_notification(user_name, other_username)
        return ok10
    else:
        return False


def delete_for_me(user_name, other_username, index):
    """
    deletes a msg for the user_name only in the chat with other_username at index
    :param user_name: the username of the user that wants to delete the msg for him
    :param other_username: the username of the user the chat is with
    :param index: the index of the msg
    :type user_name: str
    :type other_username: str
    :type index: str (but numbers '1' '2' '254' and so on)
    """
    if index.isnumeric():
        index = int(index)
    else:
        return False
    data = read_file("users.txt")
    user_password = data.split('\n')
    users = [user_password[i] for i in range(0, len(user_password), 2)]
    if user_name in users and other_username in users:
        data = read_file('chats\\' + user_name + "\\" + other_username + ".txt")
        data = data.split("#@?!#")
        if len(data) > index:
            data[index] = user_name + ": #@##@!?#Don'tDisplay"
        else:
            return False
        data = "#@?!#".join(data)
        ok = write_file('chats\\' + user_name + "\\" + other_username + ".txt", data)
        new_data = read_file('chats\\' + user_name + "\\" + "new_data.txt")
        ok2 = write_file('chats\\' + user_name + "\\" + "new_data.txt", new_data + other_username + ".txt\n")
        return ok and ok2
    else:
        return False


def delete_for_all(user_name, other_username, index):
    """
    deletes a msg for the user_name and the other_username
    :param user_name: the username of the user that wants to delete his the msg
    :param other_username: the username of the user the chat is with
    :param index: the index of the msg
    :type user_name: str
    :type other_username: str
    :type index: str (but numbers '1' '2' '254' and so on)
    """
    if index.isnumeric():
        index = int(index)
    else:
        return False
    data = read_file("users.txt")
    user_password = data.split('\n')
    users = [user_password[i] for i in range(0, len(user_password), 2)]
    if user_name in users and other_username in users:
        # change for user
        data = read_file('chats\\' + user_name + "\\" + other_username + ".txt")
        data = data.split("#@?!#")
        if len(data) > index and data[index].startswith(user_name):
            data[index] = user_name + ": #@##@!?#This Message Was Deleted."
        else:
            return False
        data = "#@?!#".join(data)
        ok = write_file('chats\\' + user_name + "\\" + other_username + ".txt", data)
        new_data = read_file('chats\\' + user_name + "\\" + "new_data.txt")
        ok2 = write_file('chats\\' + user_name + "\\" + "new_data.txt", new_data + other_username + ".txt\n")
        # change for other user
        data = read_file('chats\\' + other_username + "\\" + user_name + ".txt")
        data = data.split("#@?!#")
        if len(data) > index:
            for i in range(0, len(data)):
                if "#@?!?##*" in data[i]:
                    index += 1
                    break
                if i == index:
                    break
            if data[index].startswith(user_name):
                data[index] = user_name + ": #@##@!?#This Message Was Deleted."
        else:
            return False
        data = "#@?!#".join(data)
        ok3 = write_file('chats\\' + other_username + "\\" + user_name + ".txt", data)
        new_data = read_file('chats\\' + other_username + "\\" + "new_data.txt")
        ok4 = write_file('chats\\' + other_username + "\\" + "new_data.txt", new_data + user_name + ".txt\n")
        return ok and ok2 and ok3 and ok4
    else:
        return False


def reset_connected_users_and_where():
    """
    resets the file that contains the users that are online
    and the file that shows the chat that the user is in
    """
    write_file("connected_users.txt", "")
    write_file('where.txt', '')


def check_connected_users():
    """
    checks if all the clients in the open_client_sockets are still connected
    if someone disconnected it will remove him from the connected_users.txt file
    """
    data = read_file("users.txt")
    user_password = data.split('\n')
    all_users = [user_password[i] for i in range(0, len(user_password), 2)]
    connected_users = read_file("connected_users.txt").split("#@!#")
    while "" in connected_users:
        connected_users.remove("")
    for user in connected_users:
        still_connected = False
        for s in open_client_sockets:
            if str(s.getpeername()[0]) in user and str(s.getpeername()[1]) in user:
                still_connected = True
                break
        if not still_connected:
            # the username of the disconnected users
            d_user = user.split("=")[0]
            if d_user != "":
                users = os.listdir("chats\\" + d_user + "\\")
                users.remove("new_data.txt")
                # remove the user from the where.txt file
                data = read_file('where.txt').split("\n")
                for i in range(0, len(data)):
                    if data[i].startswith(d_user + " = "):
                        remove_unread_messages_notification(data[i].split(" = ")[0], data[i].split(" = ")[1])
                        del data[i]
                        break
                write_file('where.txt', "\n".join(data))
                # get all the files in the user library in order to update only those who know the user
                known_users_to_the_user = os.listdir("chats\\" + d_user + "\\")
                for u in users:
                    u = u[:-4]  # deletes the '.txt'
                    if u in all_users and u + ".txt" in known_users_to_the_user:
                        new_data = read_file("chats\\" + u + "\\" + "new_data.txt")
                        write_file("chats\\" + u + "\\" + "new_data.txt", new_data + "connected_users.txt\n")
            del connected_users[connected_users.index(user)]
            last_seen = read_file('last_seen.txt')
            last_seen = last_seen.split('#@!#')
            d_user_last_seen = d_user + " = " + datetime.now().strftime("%m/%d/%Y, %H:%M")
            last_seen.append(d_user_last_seen)
            write_file('last_seen.txt', '#@!#'.join(last_seen))
    if len(connected_users) == 1:
        connected_users.append("")
    write_file("connected_users.txt", "#@!#".join(connected_users))


def error_list(d_list):
    """
    handles the sockets that had an error
    :param d_list: the list of disconnected users sockets
    :type d_list: list of sockets
    """
    for current_socket in d_list:
        print("Connection With: %s:%s Is Over" % (current_socket.getpeername()[0],
                                                  current_socket.getpeername()[1]))
        logging.info("Connection With: %s:%s Is Over (error_list)" % (current_socket.getpeername()[0],
                                                                      current_socket.getpeername()[1]))
        if current_socket in open_client_sockets:
            open_client_sockets.remove(current_socket)
        try:
            current_socket.close()
        except Exception as err:
            print(str(err), "(error_list)")
            logging.warning(str(err) + " (error_list)")


def send_list(w_list):
    """
    sends all the messages in the messages_to_send if the client is available to receive data
    :param w_list: the list of available clients to receive data
    :type w_list: list of sockets
    """
    global messages_to_send
    for message in messages_to_send:
        if len(message) == 2:  # sync message
            current_socket, data = message
            if current_socket in w_list:
                try:
                    while len(data) > 0:
                        d = current_socket.send(data)
                        data = data[d:]
                except Exception as err:
                    print(str(err), "(send_list p1)")
                    logging.warning(str(err) + " (send_list p1)")
                    print("Connection With: %s:%s Is Over" % (current_socket.getpeername()[0],
                                                              current_socket.getpeername()[1]))
                    logging.warning("Connection With: %s:%s Is Over" % (current_socket.getpeername()[0],
                                                                        current_socket.getpeername()[1]))
                    if current_socket in open_client_sockets:
                        open_client_sockets.remove(current_socket)
                    current_socket.close()
        else:  # every thing except syncing messages
            current_socket, data, user_name = message
            if current_socket in w_list:
                try:
                    data_to_send = ""
                    for char in data:
                        data_to_send += str(ord(char)) + ","
                    len_and_username = str(len(data_to_send)).ljust(16) + user_name.rjust(16, '#')
                    while len(len_and_username) > 0:
                        d = current_socket.send(len_and_username.encode())
                        len_and_username = len_and_username[d:]
                    while len(data_to_send) > 0:
                        d = current_socket.send(data_to_send.encode())
                        data_to_send = data_to_send[d:]
                except Exception as err:
                    print(str(err), "(send_list p2)")
                    logging.warning(str(err) + " (send_list p2)")
                    print("Connection With: %s:%s Is Over" % (current_socket.getpeername()[0],
                                                              current_socket.getpeername()[1]))
                    logging.warning("Connection With: %s:%s Is Over" % (current_socket.getpeername()[0],
                                                                        current_socket.getpeername()[1]))
                    if current_socket in open_client_sockets:
                        open_client_sockets.remove(current_socket)
                    current_socket.close()
    messages_to_send = []


def read_list(r_list, server_socket):
    """
    receives a message from a client and calls the right function to handle it
    also excepts new clients
    :param r_list: list of clients sockets available to receive data from
    :param server_socket: the socket of the server in order to receive new clients
    :type r_list: list of sockets
    :type server_socket: socket.socket
    """
    global messages_to_send
    for current_socket in r_list:
        if current_socket is server_socket:
            try:
                client_socket, client_address = current_socket.accept()
                open_client_sockets.append(client_socket)
                print("New Connection With: %s:%s" % (str(client_address[0]), str(client_address[1])))
                logging.info("New Connection With: %s:%s" % (str(client_address[0]), str(client_address[1])))
            except Exception as err:
                print(str(err), "(read_list)")
                logging.warning(str(err) + " (read_list)")
        else:
            data, stop = receive(current_socket)
            if stop:
                continue
            cmd, fields, data_of_fields = disassemble_protocol(data)
            if cmd == "sync":
                sync(data_of_fields[0], data_of_fields[1], current_socket)
            elif cmd == "read":
                read(data_of_fields[0], data_of_fields[1])
            elif cmd == "send_msg":
                ok = send_message(data_of_fields[0], data_of_fields[1], data_of_fields[2])
                data_to_send = assemble_protocol(1, ["ok"], [ok])
                messages_to_send.append((current_socket, data_to_send, data_of_fields[0]))
            elif cmd == "chat_with":
                can_chat, message = chat_with(data_of_fields[0], data_of_fields[1])
                data_to_send = assemble_protocol(2, ["can_chat", "msg"], [can_chat, message])
                messages_to_send.append((current_socket, data_to_send, data_of_fields[0]))
            elif cmd == "upload_file":
                upload_file(data_of_fields[0], data_of_fields[1], data_of_fields[2], data_of_fields[3], current_socket)
            elif cmd == "signup":
                signup_status, user_name, status_data = sign_up(data_of_fields[0], data_of_fields[1])
                data_to_send = assemble_protocol(3, ["signup_status", "user_name", "status_data"],
                                                 [signup_status, user_name, status_data])
                messages_to_send.append((current_socket, data_to_send, user_name))
            elif cmd == "login":
                login_status, user_name, status_data = log_in(data_of_fields[0], data_of_fields[1],
                                                              current_socket)
                data_to_send = assemble_protocol(3, ["login_status", "user_name", "status_data"],
                                                 [login_status, user_name, status_data])
                messages_to_send.append((current_socket, data_to_send, user_name))
            elif cmd == "delete_for_me":
                status = delete_for_me(data_of_fields[0], data_of_fields[1], data_of_fields[2])
            elif cmd == "delete_for_all":
                status = delete_for_all(data_of_fields[0], data_of_fields[1], data_of_fields[2])


def main():
    # Logging dir and configuration
    if not os.path.isdir(LOG_DIR):
        os.makedirs(LOG_DIR)
    logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)
    # check that all the folders and files that are needed exist and if not creates them
    if not os.path.isfile('users.txt'):
        write_file('users.txt', '')
    if not os.path.isfile('where.txt'):
        write_file('where.txt', '')
    if not os.path.isfile('last_seen.txt'):
        write_file('last_seen.txt', '')
    if not os.path.isdir('chats'):
        os.mkdir('chats')
    print("Setting up server...")
    logging.info("Setting up server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        start_server(server_socket)
        while True:
            check_connected_users()
            r_list, w_list, d_list = select.select([server_socket] + open_client_sockets,
                                                   open_client_sockets, open_client_sockets)
            try:
                error_list(d_list)
                read_list(r_list, server_socket)
                send_list(w_list)
            except Exception as err:  # in case the server gets a msg that he doesn't suppose to
                print(str(err), "(main, handling a msg)")
                logging.warning(str(err) + " (main, handling a msg)")
    except Exception as err:
        print(str(err), "(main)")
        logging.warning(str(err) + " (main)")
    finally:
        server_socket.close()


if __name__ == '__main__':
    while True:
        try:
            assert disassemble_protocol("send_msg#@?#3#@?#user_name#@?#chat_with#@?#msg#@?#Omer#@?#L#@?#hello") == \
                   ("send_msg", ["user_name", "chat_with", "msg"], ["Omer", "L", "hello"])
            assert assemble_protocol(1, ["ok"], ["True"]) == "1#@?#ok#@?#True"
            reset_connected_users_and_where()  # resets the connected_users and where files
            assert read_file("connected_users.txt") == ""
            assert read_file('where.txt') == ""
            main()
        except Exception as err:
            open_client_sockets = []
            messages_to_send = []
            print(str(err), "(if __name__ == __main__)")
            logging.warning(str(err) + " (if __name__ == __main__)")
