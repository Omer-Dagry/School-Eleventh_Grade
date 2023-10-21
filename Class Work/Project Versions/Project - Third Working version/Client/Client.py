from typing import Tuple, Union, Any
from EncryptDecrypt import encrypt, decrypt
import shutil
import socket
import logging
import os
from threading import Thread
import time
from tkinter import *
from tkinter import scrolledtext
from tkinter import filedialog


PORT = 8822
IP = "127.0.0.1"
R_SIZE = 16
ALLOWED = "abcdefghijklmnopqrstuvwxyz " \
          "ABCDEFGHIJKLMNOPQRSTUVWXYZ" \
          "`1234567890-=~!@#$%^&*()_+'" \
          '|\\?/><}{][.,":;' \
          'אבגדהוזחטיכלמנסעפצקרשתםןךץף'
USERNAME_ALLOWED_CHARS = "abcdefghijklmnopqrstuvwxyz " \
                         "ABCDEFGHIJKLMNOPQRSTUVWXYZ" \
                         "`1234567890_-,;:"
chat_scrolledtext = []
chat_data = []
chat_name = []
chat_button = []
all_chats_text = []
all_chats_button = []
global user_name, msg_box, my_socket, current_chat_text, main_window, gui_status,\
    chat_buttons, current_chat, search_username, current_chat_name


class MainWindow:
    def __init__(self, size="980x520", state="zoomed", min_size=(980, 520), window_name="#"):
        global user_name
        if window_name == "#":
            window_name = user_name
        # Create Window
        self.root = Tk()
        # Configure Window
        self.root.title("Chats - " + window_name)  # title of window
        self.root.iconbitmap("chat.ico")  # icon of window
        self.root.minsize(min_size[0], min_size[1])  # minimum size of window
        self.root.geometry(size)  # default size of window
        if state == "zoomed":
            self.root.state(state)  # open window in full-screen windowed
        self.root.config(bg="#050c29")  # background color of window
        # Resize widgets with window
        self.root.columnconfigure(2, weight=1)
        self.root.rowconfigure((1, 2), weight=1)
        self.widgets = []

    def get_root(self):
        return self.root

    def get_widgets(self):
        return self.widgets

    def add_widget(self, widget, row, column, rowspan=1, columnspan=1, sticky=''):
        self.widgets.append(widget)
        self.widgets[self.widgets.index(widget)].grid(row=row, column=column, rowspan=rowspan,
                                                      columnspan=columnspan, sticky=sticky)

    def remove_widget(self, widget):
        self.widgets[self.widgets.index(widget)].grid_remove()

    def pack_widget(self, widget):
        self.widgets.append(widget)
        self.widgets[self.widgets.index(widget)].pack()

    def update(self):
        self.root.update()

    def close_window(self):
        self.root.destroy()


class ChatButtons:
    def __init__(self):
        global main_window
        self.buttons = scrolledtext.ScrolledText(main_window.get_root())  # text window for all the chats buttons
        self.buttons.config(state=DISABLED, width=36, borderwidth=5, height=27, bg="#202021")
        self.buttons.bind('<MouseWheel>', lambda: mouse_wheel_buttons(self.buttons))

    def get_chatbuttons(self):
        return self.buttons

    def add_button(self, button):
        self.buttons.insert("end", "\r\n")
        button.bind('<MouseWheel>', lambda: mouse_wheel_buttons(self.buttons))
        self.buttons.window_create("end", window=button)

    def remove_all_buttons(self):
        for widget in self.buttons.winfo_children():
            widget.destroy()


class EntryBox:
    def __init__(self, master, w=1, borderwidth=1, bg="#ffffff", fg="#000000", font=("helvetica", 16)):
        self.entry = Entry(master, width=w, borderwidth=borderwidth, bg=bg, fg=fg, font=font)

    def get_entry(self):
        return self.entry

    def insert(self, text):
        self.entry.insert("end", text)

    def clear(self):
        self.entry.delete(0, END)

    def get_text(self):
        return self.entry.get()

    def bind(self, button, func):
        self.entry.bind(button, func)


class Buttonn:
    def __init__(self, master, w=1, h=1, borderwidth=1, bg="#ffffff", fg="#000000", font=("helvetica", 16),
                 text="", command=None, state=NORMAL, image=None, justify="left"):
        self.button = Button(master, width=w, height=h, borderwidth=borderwidth, fg=fg, font=font, text=text,
                             command=command, bg=bg, state=state, image=image, justify=justify)

    def get_button(self):
        return self.button

    def get_button_text(self):
        return self.button["text"]

    def change_text(self, text):
        self.button.config(state=ACTIVE, text=text)
        self.button.config(state=DISABLED)

    def change_state(self, state):
        self.button.config(state=state)

    def change_command(self, new_command):
        self.button.config(command=new_command)


class Labell:
    def __init__(self, master, text, bg="#ffffd0", font=("helvetica", 16), justify="left"):
        self.label = Label(master, text=text, bg=bg, font=font, justify=justify)

    def get_label(self):
        return self.label


class ChatWindow:
    def __init__(self, master, state=DISABLED, bg="#282829", borderwidth=0, w=80, h=39, font=('helvetica', '16')):
        self.txt = scrolledtext.ScrolledText(master)
        self.txt.configure(state=state, bg=bg, borderwidth=borderwidth, width=w, height=h, font=font)
        self.txt.bind('<MouseWheel>', mouse_wheel_texts)  # enable to scroll with mouse wheel
        self.txt.tag_configure("tag-left", justify="left")
        self.txt.tag_configure("tag-right", justify="right")
        self.txt.yview_pickplace("end")

    def get_chatwindow(self):
        return self.txt

    def change_state(self, state):
        self.txt.config(state=state)

    def insert(self, text, tag=""):
        if tag != "":
            self.txt.insert("end", text, tag)

    def insert_label_right(self, text):
        label = Labell(self.txt, text)
        self.change_state(NORMAL)
        self.insert("\n ", tag="tag-right")
        self.txt.window_create("end", window=label.get_label())
        self.insert("                                    \n", tag="tag-left")
        self.change_state(DISABLED)

    def insert_label_left(self, text):
        label = Labell(self.txt, text, bg="#d0ffff")
        self.change_state(NORMAL)
        self.insert("\n                                    ", tag="tag-left")
        self.txt.window_create("end", window=label.get_label())
        self.insert("\n", tag="tag-left")
        self.change_state(DISABLED)

    def insert_button_right(self, text, command):
        button = Buttonn(self.txt, text=text, bg="#0e7a0c", font=("helvetica", 16), justify="left", w=30,
                         command=command)
        self.change_state(NORMAL)
        self.insert("\n ", tag="tag-right")
        self.txt.window_create("end", window=button.get_button())
        self.insert("                                    \n", tag="tag-left")
        self.change_state(DISABLED)

    def insert_button_left(self, text, command):
        button = Buttonn(self.txt, text=text, bg="#0e7a0c", font=("helvetica", 16), justify="left", w=30,
                         command=command)
        self.change_state(NORMAL)
        self.insert("\n                                    ", tag="tag-left")
        self.txt.window_create("end", window=button.get_button())
        self.insert("\n", tag="tag-left")
        self.change_state(DISABLED)

    def go_to_end(self):
        self.txt.yview_pickplace("end")


def mouse_wheel_texts(event):
    global current_chat_text
    """ scroll with mouse wheel """
    if event.delta == -120:
        current_chat_text.yview_scroll(0.1, "pixels")
    if event.delta == 120:
        current_chat_text.yview_scroll(0.1, "pixels")


def mouse_wheel_buttons(buttons, event=None):
    """ scroll with mouse wheel """
    if event.delta == -120:
        buttons.yview_scroll(1, "units")
    if event.delta == 120:
        buttons.yview_scroll(-1, "units")


def search_delete_on_click(event=None):
    global search_username
    text = search_username.get_text()
    if text == "Start a new chat" or "The User Name" in text and "Doesn't Exist" in text \
            or text == "Please Type A User Name":
        search_username.clear()
        search_username.insert('')


def message_delete_on_click(event=None):
    global msg_box
    text = msg_box.get_text()
    if text == "Type Something To Send...":
        msg_box.clear()
        msg_box.insert('')


def enter_key(event=None):
    global user_name, msg_box, current_chat
    if len(event.char) > 0 and ord(event.char) == 13:
        send_message(current_chat.get_button_text(), msg_box.get_entry())


def display_file(file_name, event=None):
    global user_name
    location = os.path.abspath(__file__).split("\\")
    del location[-1]
    location = "\\".join(location)
    location += "\\" + user_name + "\\" + file_name
    os.startfile(location)


def update_gui():
    global user_name, msg_box, current_chat_text, main_window, chat_buttons,\
        current_chat, search_username, current_chat_name, all_chats_button, all_chats_text
    chat_buttons.remove_all_buttons()
    all_chats_button = []
    main_window.remove_widget(current_chat_text.get_chatwindow())
    all_chats_text = []
    chats_name = []
    chats_data = []
    for chat_name in os.listdir(user_name + "\\"):
        if chat_name.endswith(".txt") and not any(char.isdigit() for char in chat_name)\
                and "file_count_" not in chats_name:
            chats_name.append(chat_name[:-4])
            file = open(user_name + "\\" + chat_name, encoding="utf-8")
            chat_data = file.read()
            file.close()
            chat_data = "\n".join(chat_data.split("#@?!#"))
            chats_data.append(chat_data)
    if "connected_users" in chats_name:
        del chats_data[chats_name.index("connected_users")]
        chats_name.remove("connected_users")
    for data in chats_data:
        sctxt = ChatWindow(main_window.get_root())
        msgs = data.split("\n")
        del msgs[-1]
        while "" in msgs:
            msgs.remove("")
        for msg in msgs:
            if msg.startswith(user_name):  # insert all text of the user
                if "#@??##" not in msg:
                    msg = msg[len(user_name) + 1:]
                    seen = ""
                    if "#@!#(seen at " in msg:
                        seen = "\n " + msg[-1:-31:-1][::-1]
                        msg = msg[:-34]
                    if len(msg) > 50:
                        m = msg
                        msg = ""
                        count = 0
                        for char in m:
                            if count == 50:
                                msg += " \n " + char
                                count = 0
                            else:
                                msg += char
                            count += 1
                    msg += seen
                    sctxt.insert_label_right(msg)
                else:
                    file_name = msg.split("#@??##")[-1]
                    seen = ""
                    if "#@!#(seen at " in file_name:
                        seen = "\n" + file_name.split("#@!#")[1]
                        file_name = file_name.split("#@!#")[0]
                    sctxt.insert_button_right(text=file_name + seen, command=lambda: display_file(file_name))
            else:  # insert all texts of the other user
                if "#@??##" not in msg:
                    msg = msg.split(":")
                    del msg[0]
                    msg = ":".join(msg)
                    if len(msg) > 50:
                        m = msg
                        msg = ""
                        count = 0
                        for char in m:
                            if count == 50:
                                msg += " \n " + char
                                count = 0
                            else:
                                msg += char
                            count += 1
                    sctxt.insert_label_left(text=msg)
                else:
                    file_name = msg.split("#@??##")[-1]
                    sctxt.insert_button_left(text=file_name, command=lambda: display_file(file_name))
        sctxt.go_to_end()
        all_chats_text.append(sctxt)
        if chats_name[chats_data.index(data)] == current_chat_name:
            main_window.add_widget(sctxt.get_chatwindow(), row=1, column=2, sticky='news')
            # change chat title
            file = open(user_name + "\\connected_users.txt", encoding='utf-8')
            connected_users = file.read()
            file.close()
            t = current_chat_name
            if current_chat_name in connected_users:
                t += " (Online)"
            main_window.remove_widget(current_chat_text.get_chatwindow())
            current_chat.change_text(t)
            current_chat_text = sctxt
    for i in range(0, len(chats_name)):
        def clicked(x=i):
            global main_window, current_chat_text, current_chat_name
            # new_data()
            # Remove current text from the screen
            main_window.remove_widget(current_chat_text.get_chatwindow())
            # Places the chosen text on the screen
            # ct = all_chats_text[all_chats_button[x]["text"]]
            ct = all_chats_text[x]
            main_window.add_widget(ct.get_chatwindow(), row=1, column=2, sticky='news')
            current_chat_text = ct  # Updates the variable of current text displayed
            current_chat_name = all_chats_button[x].get_button_text()
            # change chat title
            file = open(user_name + "\\connected_users.txt", encoding='utf-8')
            connected_users = file.read()
            file.close()
            t = current_chat_name
            if t in connected_users:
                t += " (Online)"
            current_chat.change_text(text=t)
        chat = chats_name[i]
        chat_button = Buttonn(chat_buttons.get_chatbuttons(), text=chat, w=33, command=clicked, font="30", bg="#202021",
                              fg="white")
        chat_buttons.add_button(chat_button.get_button())
        all_chats_button.append(chat_button)


def create_socket():
    """
    creates a socket with the constants IP & PORT
    :return: the socket
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((IP, PORT))
    except ConnectionRefusedError as error:
        s.close()
        logging.warning("   Error: " + str(error))
        print("Error: couldn't connect to server.\nClosing program.")
        exit()
    logging.info("    Connected to server.")
    return s


def assemble_protocol_and_send(cmd, number_of_fields, fields, data_of_fields, user_name,
                               file_data=b'', mode='', s=None):
    """
    assembles a message according to the protocol and sends it
    :param cmd: the command the server will handel
    :param number_of_fields: the number of data fields
    :param fields: the name of each field
    :param data_of_fields: the data of each field
    :param user_name: the user_name of the user
    :param file_data:
    :param mode:
    :param s:
    """
    if s is None:
        global my_socket
        s = my_socket
    if mode == "upload_file":
        s.send(file_data)
    else:
        data = cmd + "#@?#" + str(number_of_fields) + "#@?#"
        for field in fields:
            data += field + "#@?#"
        for f_data in data_of_fields:
            data += f_data + "#@?#"
        data = data[:-4]
        data_to_send = ""
        for char in data:
            data_to_send += str(ord(char)) + ","
        # data_to_send = encrypt(data_to_send, ord(user_name[0]))
        len_and_username = str(len(data_to_send)).ljust(16) + user_name.rjust(16, '#')
        s.send(len_and_username.encode())
        s.send(data_to_send.encode())


def receive_and_disassemble_protocol(cmd=''):
    """
    receives a message according to the protocol and disassembles it
    :return: the fields and the data of fields from the msg
    """
    global my_socket
    if cmd == "sync":
        pass
    else:
        data = ""
        left_to_receive = R_SIZE
        while left_to_receive > 0:
            data += my_socket.recv(1).decode()
            left_to_receive -= 1
        user_name = ""
        left_to_receive = R_SIZE
        while left_to_receive > 0:
            user_name += my_socket.recv(1).decode()
            left_to_receive -= 1
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
            data += my_socket.recv(1).decode()
            data_len -= 1
        # data = decrypt(data, ord(user_name[0]))
        char_val = data.split(',')
        data = ""
        for val in char_val:
            if val.isnumeric():
                data += chr(int(val))
        data_list = data.split('#@?#')
        if data_list[0].isnumeric():
            number_of_fields = int(data_list[0])
            fields = [data_list[i] for i in range(1, number_of_fields + 1)]
            data_of_fields = [data_list[i] for i in range(number_of_fields + 1, len(data_list))]
            return fields, data_of_fields
        else:
            return ["No Changes"], ["No Changes"]


def log_in():
    """
    asks for user name and password, send to server, returns server answer
    :return: True/False, the user name that the user typed, a msg that says if login is successful or not
    """
    user_name = input("Enter Your User Name: ")
    username_flag = True
    while username_flag:
        for i in range(0, len(user_name)):
            char = user_name[i]
            if char not in USERNAME_ALLOWED_CHARS:
                print("You entered a char that is not allowed, allowed chars: " + USERNAME_ALLOWED_CHARS)
                user_name = input("Enter Your User Name:")
                break
            else:
                if i == len(user_name) - 1:
                    username_flag = False
    password = input("Enter Your Password: ")
    password_flag = True
    while password_flag:
        for i in range(0, len(password)):
            char = password[i]
            if char not in USERNAME_ALLOWED_CHARS:
                print("You entered a char that is not allowed, allowed chars: " + USERNAME_ALLOWED_CHARS)
                password = input("Enter Your Password:")
                break
            else:
                if i == len(password) - 1:
                    password_flag = False
    assemble_protocol_and_send("login", 2, ["user_name", "password"], [user_name, password], user_name)
    fields, data_of_fields = receive_and_disassemble_protocol()
    if data_of_fields[0] == 'True':
        return True, user_name, data_of_fields[2]
    else:
        return False, user_name, data_of_fields[2]


def sign_up():
    """
    asks for user name and password, send to server, returns server answer
    :return: True/False, the user name that the user typed, a msg that says if signup is successful or not
    """
    user_name = input("Enter Your User Name: ")
    username_flag = True
    while username_flag:
        for i in range(0, len(user_name)):
            char = user_name[i]
            if char not in USERNAME_ALLOWED_CHARS:
                print("You entered a char that is not allowed, allowed chars: " + USERNAME_ALLOWED_CHARS)
                user_name = input("Enter Your User Name:")
                break
            else:
                if i == len(user_name) - 1:
                    username_flag = False
    password = input("Enter Your Password: ")
    password_flag = True
    while password_flag:
        for i in range(0, len(password)):
            char = password[i]
            if char not in USERNAME_ALLOWED_CHARS:
                print("You entered a char that is not allowed, allowed chars: " + USERNAME_ALLOWED_CHARS)
                password = input("Enter Your Password:")
                break
            else:
                if i == len(password) - 1:
                    password_flag = False
    assemble_protocol_and_send("signup", 2, ["user_name", "password"], [user_name, password], user_name)
    fields, data_of_fields = receive_and_disassemble_protocol()
    if data_of_fields[0] == 'True':
        return True, user_name, data_of_fields[2]
    else:
        return False, user_name, data_of_fields[2]


def sync(sync_socket, first_time=False):
    """
    syncs all files of user with the server
    :param user_name: the user_name of the user
    :param first_time:
    :return: True if there is new data else False
    """
    global current_chat_name, user_name
    first_time = str(first_time)
    assemble_protocol_and_send("sync", 2, ["user_name", "first_time"],
                               [user_name, first_time],user_name, s=sync_socket)
    # chats_name_and_len, chats_data = receive_and_disassemble_protocol(cmd="sync")
    data = ""
    left_to_receive = R_SIZE
    while left_to_receive > 0:
        data += sync_socket.recv(1).decode()
        left_to_receive -= 1
    number_of_chats = ""
    for char in data:
        if char.isnumeric():
            number_of_chats += char
    number_of_chats = int(number_of_chats)
    chats_name_and_len = []
    chats_data = []
    while number_of_chats > 0:
        left_to_receive = 20
        chat = ""
        data_len = ""
        while left_to_receive > 0:
            chat += sync_socket.recv(1).decode()
            left_to_receive -= 1
        left_to_receive = R_SIZE
        while left_to_receive > 0:
            data_len += sync_socket.recv(1).decode()
            left_to_receive -= 1
        while chat[-1] == ' ':
            chat = chat[:-1]
        while data_len[-1] == ' ':
            data_len = data_len[:-1]
        chats_name_and_len.append((chat, data_len))
        number_of_chats -= 1
    for chat_name_and_len in chats_name_and_len:
        c_name, c_len = chat_name_and_len
        c_data = b''
        left_to_receive = int(c_len)
        while left_to_receive > 0:
            c_data += sync_socket.recv(1)
            left_to_receive -= 1
        chats_data.append(c_data)
    if current_chat_name != "Home":
        user_read_msg(user_name, current_chat_name)
    if b"No Changes" != chats_data[0]:
        if not os.path.isdir(user_name):
            os.mkdir(user_name)
        for i in range(0, len(chats_data)):
            file = open(user_name + "\\" + chats_name_and_len[i][0], 'wb')
            file.write(chats_data[i])
            file.close()
        return True
    else:
        return False


def send_message(chat_with, msg_box):
    """
    every time the user send a msg we need to sync with server
    :param user_name: the user_name of the user
    :param chat_with: the user_name of the person the msg is for
    :param msg_box: the msg box in the gui
    """
    global user_name
    if " (Online)" in chat_with:
        chat_with = chat_with[:-9]
    msg = msg_box.get()
    i = 0
    while i < len(msg):
        if msg[i] not in ALLOWED:
            msg = msg[:i] + msg[i+1:]
            i -= 1
        i += 1
    if "" == msg:
        msg_box.delete(0, END)
        msg_box.insert("end", "Type Something To Send...")
    elif "#@?#" in msg:
        msg_box.delete(0, END)
        msg_box.insert("end", "Can't Send This Sequence '#@?#'.")
    elif "#@?!#" in msg:
        msg_box.delete(0, END)
        msg_box.insert("end", "Can't Send This Sequence '#@?!#'.")
    elif "#@!#" in msg:
        msg_box.delete(0, END)
        msg_box.insert("end", "Can't Send This Sequence '#@!#'.")
    elif "#@??##" in msg:
        msg_box.delete(0, END)
        msg_box.insert("end", "Can't Send This Sequence '#@??##'.")
    else:
        msg_box.delete(0, END)
        assemble_protocol_and_send("send_msg", 3, ["user_name", "chat_with", "msg"],
                                   [user_name, chat_with, msg], user_name)
        fields, data_of_fields = receive_and_disassemble_protocol()


def user_read_msg(user_name, other_username):
    assemble_protocol_and_send("read", 2, ["user_name", "other_username"], [user_name, other_username], user_name)
    fields, data_of_fields = receive_and_disassemble_protocol()


def new_data(user_name):
    assemble_protocol_and_send("new_data", 1, ["user_name"], [user_name], user_name)
    fields, data_of_fields = receive_and_disassemble_protocol()


def sync_():
    global chat_data, user_name
    sync_socket = create_socket()
    sync(sync_socket, first_time=True)
    update_gui()
    while True:
        new_data = sync(sync_socket)
        if new_data:
            update_gui()
        time.sleep(0.2)


def upload_file__(other_username, event=None):
    global upload_thread
    upload_thread = Thread(target=upload_file, args=(other_username,), daemon=True)
    upload_thread.start()


def upload_file(other_username):
    """
    """
    global user_name
    if " (Online)" in other_username:
        other_username = other_username[:-9]
    if other_username != "Home":
        filename = filedialog.askopenfilename()
        if filename != "":
            upload_socket = create_socket()
            file = open(filename, 'rb')
            file_data = file.read()
            file.close()
            file_size = str(len(file_data))
            file_ends_with = '.' + filename.split('.')[-1]
            assemble_protocol_and_send("upload_file", 4, ["user_name", "other_username", "file_size", "filename.?"],
                                       [user_name, other_username, file_size, file_ends_with], user_name,
                                       s=upload_socket)
            # my_socket.send(file_data)
            assemble_protocol_and_send("upload_file", 4, ["user_name", "other_username", "file_size", "filename.?"],
                                       [user_name, other_username, file_size, file_ends_with], user_name,
                                       file_data, mode="upload_file", s=upload_socket)
            fields, data_of_fields = receive_and_disassemble_protocol()
            upload_socket.close()


def login_gui():
    pass


def signup_gui():
    pass


def login_signup_gui():
    pass


def gui():
    global user_name, msg_box, main_window, chat_buttons, current_chat,\
        search_username, current_chat_text, current_chat_name
    # Create the gui window
    main_window = MainWindow(window_name=user_name)
    root = main_window.get_root()
    # Create a text box that will contain chats buttons
    chat_buttons = ChatButtons()
    main_window.add_widget(chat_buttons.get_chatbuttons(), row=1, column=0, columnspan=2, rowspan=2, sticky='news')
    # Create chat title (name of other username and stats)
    current_chat = Buttonn(root, text="Home", w=80, h=1, font="bold",
                           bg="#282829", fg="white", state=DISABLED)
    main_window.add_widget(current_chat.get_button(), row=0, column=2, sticky='news')
    # Create an entry box for text
    msg_box = EntryBox(root, w=121, borderwidth=3, bg="#202021", fg="white", font=("helvetica", 16))
    msg_box.get_entry().bind('<KeyPress>', enter_key)
    main_window.add_widget(msg_box.get_entry(), row=19, column=2, sticky='news')
    # Create a button to submit the input from the input box
    send_msg = Buttonn(root, text="Send", w=46, h=3, borderwidth=3, bg="#202021", fg="white", font=None,
                       command=lambda: send_message(current_chat.get_button_text(), msg_box.get_entry()))
    main_window.add_widget(send_msg.get_button(), row=19, column=0, sticky='news')
    # Create a button to upload files
    photo = PhotoImage(file="file.png")
    file_upload = Buttonn(root, image=photo, bg="#202021",
                          command=lambda: upload_file__(current_chat.get_button_text()))
    main_window.add_widget(file_upload.get_button(), row=19, column=1, sticky='news')
    chat = ChatWindow(main_window.get_root())
    main_window.add_widget(chat.get_chatwindow(), row=1, column=2, sticky='news')
    current_chat_text = chat
    current_chat_name = "Home"

    def new_chat(entry_box, my_username=user_name):
        """
        if the user_name that the user want to text with exists it will open a new chat with him
        :type entry_box: EntryBox
        """
        global current_chat_text, current_chat, current_chat_name
        other_username = entry_box.get_text()
        if other_username == "Start a new chat" or other_username == "" or other_username == "Please Type A User Name":
            entry_box.clear()
            entry_box.insert("Please Type A User Name")
        else:
            i = 0
            while i < len(other_username):
                if other_username[i] not in ALLOWED:
                    other_username = other_username[:i] + other_username[i + 1:]
                    i -= 1
                i += 1
            entry_box.clear()
            entry_box.insert("Start a new chat")
            assemble_protocol_and_send("chat_with", 2, ["user_name", "chat_with"],
                                       [my_username, other_username], user_name)
            fields, data_of_fields = receive_and_disassemble_protocol()
            if "False" in data_of_fields:
                entry_box.clear()
                entry_box.insert("The User Name '%s' Doesn't Exist" % other_username)
            else:
                current_chat_name = other_username
    # Create an input box to search a username and start chat with him
    search_username = EntryBox(root, w=40, font=None)
    search_username.bind('<Button-1>', search_delete_on_click)
    search_username.insert("Start a new chat")
    main_window.add_widget(search_username.get_entry(), row=0, column=0, sticky='news')
    # Create a button to submit the input from the input box
    search_chat = Buttonn(root, text="Search", w=8, h=1, borderwidth=3, bg="#202021", fg="white",
                          command=lambda: new_chat(search_username), font=None)
    main_window.add_widget(search_chat.get_button(), row=0, column=1, sticky='news')
    sync_thread = Thread(target=sync_, daemon=True)
    sync_thread.start()
    root.mainloop()


def main():
    global my_socket, user_name
    my_socket = create_socket()
    login_or_signup = input("Do You Have A User? [Y/N] ")
    while login_or_signup != 'Y' and login_or_signup != 'N':
        login_or_signup = input("Please Enter A Valid Answer [Y/N] ")
    if login_or_signup == 'Y':
        login_status = False
        while not login_status:
            login_status, user_name, status_data = log_in()
            print(status_data)
    else:
        signup_status = False
        while not signup_status:
            signup_status, user_name, status_data = sign_up()
            print(status_data)
        login_status = False
        while not login_status:
            login_status, user_name, status_data = log_in()
            print(status_data)
    if login_status:
        try:
            gui()
        except socket.error as err:
            print("Connection To Server Error")
        finally:
            my_socket.close()
            # Remove All The Chats From Client PC
            if os.path.isdir(user_name):
                shutil.rmtree(user_name)


if __name__ == '__main__':
    main()
