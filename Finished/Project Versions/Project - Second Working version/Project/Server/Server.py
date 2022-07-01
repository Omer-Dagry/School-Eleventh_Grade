"""
Author: Omer Dagry
Program name: Project
Description: Server
Date: 06.03.2022

Protocol:
send data len with padding (for example if len is 70 it will send '70              ')
after this send data with separation between fields & fields description & number of fields for example:
2#@?#user_name#@?#chat_with#@?#Omer Dagry#@?#Someone
"""
from time import sleep

from EncryptDecrypt import encrypt, decrypt
from datetime import datetime
import select
import shutil
import socket
import os


SERVER_PORT = 8822
SERVER_IP = "0.0.0.0"
R_SIZE = 16
send_sockets = []
open_client_sockets = []
messages_to_send = []


def start_server(server_socket):
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()
    print("Listening for clients...")


def receive(current_socket):
    try:
        stop = False
        data = ""
        left_to_receive = R_SIZE
        while left_to_receive > 0:
            data += current_socket.recv(1).decode()
            left_to_receive -= 1
            if data == "":
                open_client_sockets.remove(current_socket)
                current_socket.close()
                stop = True
                break
        if not stop:
            user_name = ""
            left_to_receive = R_SIZE
            while left_to_receive > 0:
                user_name += current_socket.recv(1).decode()
                left_to_receive -= 1
                if user_name == "":
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
                data_len = int(data_len)
                data = ""
                while data_len > 0:
                    data += current_socket.recv(1).decode()
                    data_len -= 1
                    if data == "":
                        open_client_sockets.remove(current_socket)
                        current_socket.close()
                        stop = True
                        break
                if not stop:
                    data = decrypt(data, ord(user_name[0]))
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
    except socket.error as err:
        print(str(err))
        print("Connection With: %s:%s Is Over" % (current_socket.getpeername()[0],
                                                  current_socket.getpeername()[1]))
        if current_socket in open_client_sockets:
            open_client_sockets.remove(current_socket)
        current_socket.close()
        return '', True


def disassemble_protocol(data):
    data_list = data.split('#@?#')
    cmd = data_list[0]
    del data_list[0]
    number_of_fields = int(data_list[0])
    fields = [data_list[i] for i in range(1, number_of_fields + 1)]
    data_of_fields = [data_list[i] for i in range(number_of_fields + 1, len(data_list))]
    return cmd, fields, data_of_fields


def assemble_protocol(number_of_fields, fields, data_of_fields):
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
        return None


def log_in(user_name, password, client_socket):
    data = read_file("users.txt")
    user_password = data.split('\n')
    users = [user_password[i] for i in range(0, len(user_password), 2)]
    passwords = [user_password[i] for i in range(1, len(user_password), 2)]
    if user_name in users:
        if password == passwords[users.index(user_name)]:
            data = read_file("connected_users.txt")
            data = data + "#@!#" + user_name + "=" + str(client_socket.getpeername()[0]) + ":" + \
                str(client_socket.getpeername()[1]) + "#@!#"
            write_file("connected_users.txt", data)
            for user in data.split("#@!#"):
                if user != "":
                    write_file("chats\\" + user.split('=')[0] + "\\" + "new_data.txt", "yes")
            return 'True', user_name, "Logged In Successfully"
        else:
            return 'False', user_name, "User Name Or Password Is Incorrect"
    else:
        return 'False', user_name, "User Name Or Password Is Incorrect"


def sign_up(user_name, password):
    data = read_file("users.txt")
    user_password = data.split('\n')
    users = [user_password[i] for i in range(0, len(user_password), 2)]
    if user_name in users:
        return 'False', user_name, "This User Name Is Taken"
    ok = write_file("users.txt", data + user_name + "\n" + password + "\n")
    if ok:
        user_chats_dir = 'chats\\' + user_name
        os.mkdir(user_chats_dir)
        ok = write_file(user_chats_dir + "\\" + "new_data.txt", "no")
        if ok:
            return 'True', user_name, "Signed Up Successfully"
        else:
            shutil.rmtree(user_chats_dir)
            return 'False', user_name, "Something Went wrong"
    else:
        return 'False', user_name, "Something Went wrong"


def sync(user_name, first_time, current_socket):
    global messages_to_send
    user_chats_dir = 'chats\\' + user_name
    if (read_file(user_chats_dir + "\\" + "new_data.txt") == "yes") or (first_time == 'True'):
        chats = os.listdir(user_chats_dir)
        chats.remove("new_data.txt")
        i = 0
        while i < len(chats):
            if "file_count_" in chats[i]:
                del chats[i]
                i -= 1
            i += 1
        chats_data = []
        i = 0
        while i < len(chats):
            chats_data.append(read_file(user_chats_dir + "\\" + chats[i], mode='rb'))
            i += 1
        write_file(user_chats_dir + "\\" + "new_data.txt", "no")
        chats.append("connected_users.txt")
        connected_users = read_file("connected_users.txt").split("#@!#")
        while "" in connected_users:
            connected_users.remove("")
        for user in connected_users:
            connected_users[connected_users.index(user)] = user.split('=')[0]
        chats_data.append("#@!#".join(connected_users).encode())
        data_to_send = ""
        messages_to_send.append((current_socket, str(len(chats)).ljust(16).encode()))
        for chat in chats:
            data_to_send += chat.ljust(20) + str(len(chats_data[chats.index(chat)])).ljust(16)
        messages_to_send.append((current_socket, data_to_send.encode()))
        for chat_data in chats_data:
            messages_to_send.append((current_socket, chat_data))
    else:
        messages_to_send.append((current_socket, '1'.ljust(16).encode()))
        messages_to_send.append((current_socket, ("No Changes".ljust(20) + "10".ljust(16)).encode()))
        messages_to_send.append((current_socket, b"No Changes"))


def chat_with(user_name, other_username):
    data = read_file("users.txt")
    user_password = data.split('\n')
    users = [user_password[i] for i in range(0, len(user_password), 2)]
    if other_username == "" or user_name == "":
        return 'False', ''
    if other_username in users and other_username != user_name:
        if not os.path.isfile('chats\\' + user_name + "\\" + other_username + ".txt"):
            ok = write_file('chats\\' + user_name + "\\" + other_username + ".txt", "")
            ok2 = write_file('chats\\' + other_username + "\\" + user_name + ".txt", "")
            if not (ok and ok2):
                return 'False', ''
            chat_data = ''
        else:
            chat_data = read_file('chats\\' + user_name + "\\" + other_username + ".txt")
        return 'True', chat_data
    else:
        return 'False', ''


def send_message(user_name, other_username, msg):
    if os.path.isfile('chats\\' + user_name + "\\" + other_username + ".txt") and \
            os.path.isfile('chats\\' + other_username + "\\" + user_name + ".txt"):
        write_file('chats\\' + user_name + "\\" + "new_data.txt", "yes")
        write_file('chats\\' + other_username + "\\" + "new_data.txt", "yes")
        read(user_name, other_username)
        data = read_file('chats\\' + user_name + "\\" + other_username + ".txt")
        write_file('chats\\' + user_name + "\\" + other_username + ".txt", data + user_name + ": " + msg + "#@?!#")
        data = read_file('chats\\' + other_username + "\\" + user_name + ".txt")
        write_file('chats\\' + other_username + "\\" + user_name + ".txt", data + user_name + ": " + msg + "#@?!#")
        return 'True'
    else:
        return 'False'


def read(user_name, other_username):
    data = read_file("users.txt")
    user_password = data.split('\n')
    users = [user_password[i] for i in range(0, len(user_password), 2)]
    if user_name in users and other_username in users:
        data = read_file('chats\\' + other_username + "\\" + user_name + ".txt")
        data = data.split("#@?!#")
        data_to_write = ""
        while "" in data:
            data.remove("")
        for line in data:
            if other_username in line and "#@!#" not in line:
                date_and_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                data_to_write += line + "#@!#(seen at %s)#@?!#" % date_and_time
                write_file('chats\\' + other_username + "\\" + "new_data.txt", "yes")
            else:
                data_to_write += line + "#@?!#"
        return write_file('chats\\' + other_username + "\\" + user_name + ".txt", data_to_write)
    else:
        return False


def new_data(user_name):
    return write_file('chats\\' + user_name + "\\new_data.txt", "yes")


def upload_file(user_name, other_username, file_size, file_ends_with, current_socket):
    file_size = int(file_size)
    file_data = b''
    while file_size > 0:
        file_data += current_socket.recv(1)
        file_size -= 1
    file_name_user = read_file('chats\\' + user_name + "\\" + "file_count_" + other_username + ".txt")
    file_name_other = read_file('chats\\' + other_username + "\\" + "file_count_" + user_name + ".txt")
    write_file('chats\\' + user_name + "\\" + "file_count_" + other_username + ".txt", str(int(file_name_user) + 1))
    write_file('chats\\' + other_username + "\\" + "file_count_" + user_name + ".txt", str(int(file_name_other) + 1))
    data = read_file('chats\\' + user_name + "\\" + other_username + ".txt")
    data += user_name + ": #@??##" + other_username + "_" + file_name_user + file_ends_with + "#@?!#"
    write_file('chats\\' + user_name + "\\" + other_username + ".txt", data)
    data = read_file('chats\\' + other_username + "\\" + user_name + ".txt")
    data += user_name + ": #@??##" + user_name + "_" + file_name_other + file_ends_with + "#@?!#"
    write_file('chats\\' + other_username + "\\" + user_name + ".txt", data)
    new_data(user_name)
    new_data(other_username)
    write_file('chats\\' + other_username + "\\" + user_name + "_" + file_name_other + file_ends_with,
               file_data, mode="wb")
    return write_file('chats\\' + user_name + "\\" + other_username + "_" + file_name_user + file_ends_with,
                      file_data, mode="wb")


def check_connected_users():
    data = read_file("users.txt")
    user_password = data.split('\n')
    all_users = [user_password[i] for i in range(0, len(user_password), 2)]
    connected_users = read_file("connected_users.txt").split("#@!#")
    for user in connected_users:
        still_connected = False
        for s in open_client_sockets:
            if str(s.getpeername()[0]) in user and str(s.getpeername()[1]) in user:
                still_connected = True
        if not still_connected:
            d_user = connected_users[connected_users.index(user)].split("=")[0]
            if d_user != "":
                users = os.listdir("chats\\" + d_user + "\\")
                users.remove("new_data.txt")
                for u in users:
                    u = u[:-4]
                    if u in all_users:
                        write_file("chats\\" + u + "\\" + "new_data.txt", "yes")
            del connected_users[connected_users.index(user)]
    if len(connected_users) == 1:
        connected_users.append("")
    write_file("connected_users.txt", "#@!#".join(connected_users))


def error_list(d_list):
    for current_socket in d_list:
        print("Connection With: %s:%s Is Over" % (current_socket.getpeername()[0],
                                                  current_socket.getpeername()[1]))
        if current_socket in open_client_sockets:
            open_client_sockets.remove(current_socket)
        current_socket.close()


def send_list(w_list):
    global messages_to_send
    for message in messages_to_send:
        if len(message) == 2:
            current_socket, data = message
            if current_socket in w_list:
                try:
                    current_socket.send(data)
                except socket.error as err:
                    print(str(err))
                    print("Connection With: %s:%s Is Over" % (current_socket.getpeername()[0],
                                                              current_socket.getpeername()[1]))
                    if current_socket in open_client_sockets:
                        open_client_sockets.remove(current_socket)
                    current_socket.close()
                # messages_to_send.remove(message)
        else:
            current_socket, data, user_name = message
            if current_socket in w_list:
                try:
                    data_to_send = ""
                    for char in data:
                        data_to_send += str(ord(char)) + ","
                    data_to_send = encrypt(data_to_send, ord(user_name[0]))
                    len_and_username = str(len(data_to_send)).ljust(16) + user_name.rjust(16, '#')
                    current_socket.send(len_and_username.encode())
                    current_socket.send(data_to_send.encode())
                except socket.error as err:
                    print(str(err))
                    print("Connection With: %s:%s Is Over" % (current_socket.getpeername()[0],
                                                              current_socket.getpeername()[1]))
                    if current_socket in open_client_sockets:
                        open_client_sockets.remove(current_socket)
                    current_socket.close()
                # messages_to_send.remove(message)
    messages_to_send = []


def read_list(r_list, server_socket):
    global messages_to_send
    for current_socket in r_list:
        if current_socket is server_socket:
            try:
                client_socket, client_address = current_socket.accept()
                open_client_sockets.append(client_socket)
                print("New Connection With: %s:%s" % (str(client_address[0]), str(client_address[1])))
            except socket.error as err:
                print(str(err))
        else:
            data, stop = receive(current_socket)
            if stop:
                continue
            cmd, fields, data_of_fields = disassemble_protocol(data)
            if cmd == "sync":
                sync(data_of_fields[0], data_of_fields[1], current_socket)
            elif cmd == "read":
                status_update = read(data_of_fields[0], data_of_fields[1])
                data_to_send = assemble_protocol(1, ["status_update"], [str(status_update)])
                messages_to_send.append((current_socket, data_to_send, data_of_fields[0]))
            elif cmd == "send_msg":
                ok = send_message(data_of_fields[0], data_of_fields[1], data_of_fields[2])
                data_to_send = assemble_protocol(1, ["ok"], [ok])
                messages_to_send.append((current_socket, data_to_send, data_of_fields[0]))
            elif cmd == "chat_with":
                can_chat, chat_data = chat_with(data_of_fields[0], data_of_fields[1])
                data_to_send = assemble_protocol(2, ["can_chat", "chat_data"], [can_chat, chat_data])
                messages_to_send.append((current_socket, data_to_send, data_of_fields[0]))
            elif cmd == "new_data":
                status_update = new_data(data_of_fields[0])
                data_to_send = assemble_protocol(1, ["status_update"], [str(status_update)])
                messages_to_send.append((current_socket, data_to_send, data_of_fields[0]))
            elif cmd == "upload_file":
                status_update = upload_file(data_of_fields[0], data_of_fields[1],
                                            data_of_fields[2], data_of_fields[3], current_socket)
                data_to_send = assemble_protocol(1, ["status_update"], [str(status_update)])
                messages_to_send.append((current_socket, data_to_send, data_of_fields[0]))
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


def main():
    if not os.path.isfile('users.txt'):
        file = open('users.txt', 'w')
        file.close()
    if not os.path.isdir('chats'):
        os.mkdir('chats')
    print("Setting up server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        start_server(server_socket)
        while True:
            check_connected_users()
            r_list, w_list, d_list = select.select([server_socket] + open_client_sockets,
                                                   open_client_sockets, open_client_sockets)
            error_list(d_list)
            send_list(w_list)
            read_list(r_list, server_socket)
    except socket.error as err:
        print(str(err))
    finally:
        server_socket.close()


if __name__ == '__main__':
    main()
