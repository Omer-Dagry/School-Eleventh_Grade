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

global my_socket
chat_scrolledtext = []
chat_data = []
chat_name = []
chat_button = []


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
                               file_data=b'', mode='', s="my_socket"):
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
    if s == "my_socket":
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
        data_to_send = encrypt(data_to_send, ord(user_name[0]))
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
        data = decrypt(data, ord(user_name[0]))
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
    password = input("Enter Your Password: ")
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
    user_name = input("Enter Your Desired User Name: ")
    password = input("Enter Your Password: ")
    assemble_protocol_and_send("signup", 2, ["user_name", "password"], [user_name, password], user_name)
    fields, data_of_fields = receive_and_disassemble_protocol()
    if data_of_fields[0] == 'True':
        return True, user_name, data_of_fields[2]
    else:
        return False, user_name, data_of_fields[2]


def sync(user_name, sync_socket, first_time=False):
    """
    syncs all files of user with the server
    :param user_name: the user_name of the user
    :param first_time:
    :return: True if there is new data else False
    """
    global current_chatname
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
    if current_chatname != "Home":
        user_read_msg(user_name, current_chatname)
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


def send_message(user_name, chat_with, msg_box):
    """
    every time the user send a msg we need to sync with server
    :param user_name: the user_name of the user
    :param chat_with: the user_name of the person the msg is for
    :param msg_box: the msg box in the gui
    """
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


def display_file(user_name, file_name, event=None):
    location = os.path.abspath(__file__).split("\\")
    del location[-1]
    location = "\\".join(location)
    location += "\\" + user_name + "\\" + file_name
    os.startfile(location)


def create_text_and_buttons(user_name, root):
    def mouse_wheel_texts(event):
        """ scroll with mouse wheel """
        global current_scrolledtext
        if event.delta == -120:
            current_scrolledtext.yview_scroll(0.1, "pixels")
        if event.delta == 120:
            current_scrolledtext.yview_scroll(0.1, "pixels")

    chat_name = []
    chat_data = []
    for file_name in os.listdir(user_name + "\\"):
        if file_name.endswith(".txt"):
            file = open(user_name + "\\" + file_name, encoding='utf-8')
            file_data = file.read()
            file.close()
            file_data = "\n".join(file_data.split("#@?!#"))
            chat_data.append(file_data)
            chat_name.append(file_name[:-4])
    # Create a non-editable text with scroll bar for each chat & append it to a list of all chats texts
    if "connected_users" in chat_name:
        del chat_data[chat_name.index("connected_users")]
        chat_name.remove("connected_users")
    if "uploaded_file_count" in chat_name:
        del chat_data[chat_name.index("uploaded_file_count")]
        chat_name.remove("uploaded_file_count")
    global current_scrolledtext, current_chatname, current_chat
    current_scrolledtext.grid_remove()
    for data in chat_data:
        sctxt = scrolledtext.ScrolledText(root)  # create text widget
        sctxt.tag_configure("tag-left", justify="left")
        sctxt.tag_configure("tag-right", justify="right")
        msgs = data.split("\n")
        del msgs[-1]
        while "" in msgs:
            msgs.remove("")
        for msg in msgs:
            if msg.startswith(user_name):  # insert all text of the user
                if "#@??##" not in msg:
                    msg = msg[len(user_name)+1:]
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
                    line = Label(sctxt, text=msg, bg="#ffffd0", font=("helvetica", 16), justify="left")
                else:
                    file_name = msg.split("#@??##")[-1]
                    seen = ""
                    if "#@!#(seen at " in file_name:
                        seen = "\n" + file_name.split("#@!#")[1]
                        file_name = file_name.split("#@!#")[0]
                    line = Button(sctxt, text=file_name + seen, bg="#ffffd0", font=("helvetica", 16), justify="left",
                                  command=lambda: display_file(user_name, file_name))
                sctxt.insert("end", "\n ", "tag-right")
                sctxt.window_create("end", window=line)
                sctxt.insert("end", "                                    \n")
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
                    line = Label(sctxt, text=msg + "    ", bg="#d0ffff", font=("helvetica", 16), justify="left")
                else:
                    file_name = msg.split("#@??##")[-1]
                    line = Button(sctxt, text=file_name, bg="#ffffd0", font=("helvetica", 16), justify="left",
                                  command=lambda: display_file(user_name, file_name))
                sctxt.insert("end", "\n                                    ")
                sctxt.window_create("end", window=line)
                sctxt.insert("end", "\n")
        sctxt.bind('<MouseWheel>', mouse_wheel_texts)  # enable to scroll with mouse wheel
        sctxt.configure(state=DISABLED, borderwidth=0, width=80, height=23, bg="#282829")
        sctxt['font'] = ('helvetica', '16')
        sctxt.yview_pickplace("end")
        chat_scrolledtext.append(sctxt)
        if chat_name[chat_data.index(data)] == current_chatname:
            sctxt.grid(row=1, column=2, rowspan=16, sticky="news")
            # change chat title
            file = open(user_name + "\\connected_users.txt", encoding='utf-8')
            connected_users = file.read()
            file.close()
            t = current_chatname
            if current_chatname in connected_users:
                t += " (Online)"
            current_chat.grid_remove()
            current_chat.config(state=ACTIVE, text=t)
            current_chat.config(state=DISABLED)
            current_chat.grid(row=0, column=2, sticky="news")

    def mouse_wheel_buttons(event):
        """ scroll with mouse wheel """
        if event.delta == -120:
            buttons.yview_scroll(1, "units")
        if event.delta == 120:
            buttons.yview_scroll(-1, "units")

    global buttons, chat_button
    for button in chat_button:
        button.destroy()
    chat_button = []
    buttons.destroy()
    buttons = scrolledtext.ScrolledText(root)  # text window for all the chats buttons
    buttons.config(state=DISABLED, width=36, borderwidth=4, height=26, bg="#202021")
    buttons.grid(row=1, column=0, columnspan=2, sticky='news', rowspan=2)
    buttons.bind('<MouseWheel>', mouse_wheel_buttons)
    # Create a button for each chat & append it to a list of all chats buttons
    for i in range(0, len(chat_name)):
        def clicked(x=i):
            """ if a chat button is clicked it places the corresponding chat on the screen"""
            new_data(user_name)
            ct = chat_scrolledtext[chat_name.index(chat_button[x]["text"])]
            # Remove current text from the screen
            global current_scrolledtext, current_chat, current_chatname
            current_scrolledtext.grid_remove()
            # Places the chosen text on the screen
            ct.grid(row=1, column=2, rowspan=18, sticky="news")
            current_scrolledtext = ct  # Updates the variable of current text displayed
            # change chat title
            file = open(user_name + "\\connected_users.txt", encoding='utf-8')
            connected_users = file.read()
            file.close()
            t = chat_button[x]["text"]
            if t in connected_users:
                t += " (Online)"
            current_chat.grid_remove()
            current_chat.config(state=ACTIVE, text=t)
            current_chat.config(state=DISABLED)
            current_chat.grid(row=0, column=2, sticky="news")
            current_chatname = chat_button[x]["text"]

        chat = chat_name[i]
        buttons.insert("end", "\r\n")
        button = Button(buttons, text=chat, highlightthickness=0, width=33, command=clicked,
                        font="30", bg="#202021", fg="white")
        button.bind('<MouseWheel>', mouse_wheel_buttons)
        chat_button.append(button)
        buttons.window_create("end", window=button)


def sync_(user_name, root):
    global chat_data, current_scrolledtext
    sync_socket = create_socket()
    sync(user_name, sync_socket, first_time=True)
    create_text_and_buttons(user_name, root)
    while True:
        new_data = sync(user_name, sync_socket)
        if new_data:
            create_text_and_buttons(user_name, root)
        time.sleep(0.2)


def upload_file(user_name, other_username, event=None):
    """
    """
    if other_username != "Home":
        filename = filedialog.askopenfilename()
        if filename != "":
            file = open(filename, 'rb')
            file_data = file.read()
            file.close()
            file_size = str(len(file_data))
            file_ends_with = '.' + filename.split('.')[-1]
            assemble_protocol_and_send("upload_file", 4, ["user_name", "other_username", "file_size", "filename.?"],
                                       [user_name, other_username, file_size, file_ends_with], user_name)
            # my_socket.send(file_data)
            assemble_protocol_and_send("upload_file", 4, ["user_name", "other_username", "file_size", "filename.?"],
                                       [user_name, other_username, file_size, file_ends_with], user_name,
                                       file_data, mode="upload_file")
            fields, data_of_fields = receive_and_disassemble_protocol()


def login_gui():
    pass


def signup_gui():
    pass


def login_signup_gui():
    pass


def gui(user_name):
    """
    the graphic user interface
    :param user_name: the user_name of the user
    """
    global chat_scrolledtext, chat_data, chat_name, chat_button
    root = Tk()  # Create a window
    # Configure window
    root.title("Chats - " + user_name)  # title of window
    root.iconbitmap("chat.ico")  # icon of window
    root.minsize(980, 520)  # minimum size of window
    root.geometry("980x520")  # when full screen is exited it will resize to this size (and can be resized manually)
    root.state("zoomed")  # open window in full-screen windowed
    root.config(bg="#050c29")  # background color of window

    def mouse_wheel_buttons(event):
        """ scroll with mouse wheel """
        if event.delta == -120:
            buttons.yview_scroll(1, "units")
        if event.delta == 120:
            buttons.yview_scroll(-1, "units")

    global buttons
    buttons = scrolledtext.ScrolledText(root)  # text window for all the chats buttons
    buttons.config(state=DISABLED, width=36, borderwidth=5, height=27, bg="black")
    buttons.grid(row=1, column=0, columnspan=2, sticky='news', rowspan=2)
    buttons.bind('<MouseWheel>', mouse_wheel_buttons)
    # Create an empty non-editable text with scroll for the start
    global txt
    txt = scrolledtext.ScrolledText(root)
    txt.configure(state=DISABLED, bg="#282829", borderwidth=0, width=80, height=23)
    txt['font'] = ('helvetica', '16')
    txt.grid(row=1, column=2, rowspan=18, sticky="news")
    global current_chatname
    current_chatname = "Home"
    # Sync in background, if there is new data it will recreate all the text windows and buttons
    sync_thread = Thread(target=sync_, args=(user_name, root), daemon=True)
    sync_thread.start()

    def enter_key(event):
        if len(event.char) > 0 and ord(event.char) == 13:
            send_message(user_name, current_chat['text'], msg_box)
    # Create an input box to start new chat
    msg_box = Entry(root, width=121, borderwidth=3, bg="#202021", fg="white", font=("helvetica", 16))
    msg_box.bind('<KeyPress>', enter_key)
    msg_box.grid(row=19, column=2, sticky="news")
    # Create a button to submit the input from the input box
    send_msg = Button(root, text="Send", width=46, height=1, borderwidth=3, bg="#202021", fg="white",
                      command=lambda: send_message(user_name, current_chat['text'], msg_box))
    send_msg.grid(row=19, column=0, sticky="news")
    # Global variable for the current scrolled text on the window
    global current_scrolledtext
    current_scrolledtext = txt
    # chat title
    global current_chat
    current_chat = Button(root, text="", width=80, height=1, state=DISABLED,
                          font="bold", bg="#282829", fg="white")

    def new_chat(search_user_name_box, my_username=user_name):
        """ if the user_name that the user want to text with exists it will open a new chat with him"""
        global current_scrolledtext, current_chat
        other_username = search_user_name_box.get()
        if other_username == "Start a new chat" or other_username == "" or other_username == "Please Type A User Name":
            search_username.delete(0, END)
            search_username.insert("end", "Please Type A User Name")
        else:
            i = 0
            while i < len(other_username):
                if other_username[i] not in ALLOWED:
                    other_username = other_username[:i] + other_username[i + 1:]
                    i -= 1
                i += 1
            search_username.delete(0, END)
            search_username.insert("end", "Start a new chat")
            assemble_protocol_and_send("chat_with", 2, ["user_name", "chat_with"],
                                       [my_username, other_username], user_name)
            fields, data_of_fields = receive_and_disassemble_protocol()
            if "False" in data_of_fields:
                current_scrolledtext.grid_remove()  # remove current chat from display
                no_user_textbox = scrolledtext.ScrolledText(root)  # create new chat
                no_user_textbox.insert("end", "The User Name '%s' Doesn't Exist" % other_username)  # insert msg
                no_user_textbox.configure(state=DISABLED, bg="white", borderwidth=0)
                no_user_textbox['font'] = ('helvetica', '16')
                no_user_textbox.grid(row=1, column=2, rowspan=16, sticky="news")  # place on screen
                current_scrolledtext = no_user_textbox
                # change chat title
                current_chat.grid_remove()
                current_chat.config(state=ACTIVE, text=other_username)
                current_chat.config(state=DISABLED)
                current_chat.grid(row=0, column=2, sticky="news")
            else:
                current_scrolledtext.grid_remove()  # remove current chat from display
                selected_user_textbox = scrolledtext.ScrolledText(root)  # create new chat
                selected_user_textbox.insert("end", data_of_fields[1])  # inserts data of chat
                selected_user_textbox.configure(state=DISABLED, bg="white", borderwidth=0)
                selected_user_textbox['font'] = ('helvetica', '12')
                selected_user_textbox.grid(row=1, column=2, rowspan=16, sticky="news")  # places on screen
                current_scrolledtext = selected_user_textbox
                # change chat title
                current_chat.grid_remove()
                current_chat.config(state=ACTIVE, text=other_username)
                current_chat.config(state=DISABLED)
                current_chat.grid(row=0, column=2, sticky="news")
    # Create an input box to search a username and start chat with him
    search_username = Entry(root, width=40)
    # Create a button to upload files
    photo = PhotoImage(file="file.png")
    file_upload = Button(root, image=photo, bg="#202021", command=lambda: upload_file(user_name, current_chatname))
    file_upload.grid(row=19, column=1, sticky="news")

    def search_delete_on_click(event):
        if search_username.get() == 'Start a new chat':
            search_username.delete(0, END)
            search_username.insert("end", '')
    search_username.insert("end", "Start a new chat")
    search_username.bind('<Button-1>', search_delete_on_click)
    search_username.grid(row=0, column=0, sticky="news")
    # Create a button to submit the input from the input box
    search_chat = Button(root, text="Search", width=8, height=1, borderwidth=3, bg="#202021", fg="white",
                         command=lambda: new_chat(search_username))
    search_chat.grid(row=0, column=1, sticky="news")
    root.columnconfigure(2, weight=1)
    root.rowconfigure((1, 2), weight=1)
    root.mainloop()


def main():
    global my_socket
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
            gui(user_name)
        except socket.error as err:
            print("Connection To Server Error")
        finally:
            my_socket.close()
            # Remove All The Chats From Client PC
            if os.path.isdir(user_name):
                shutil.rmtree(user_name)


if __name__ == '__main__':
    main()
