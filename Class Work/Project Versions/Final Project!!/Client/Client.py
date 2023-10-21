"""
Author: Omer Dagry
Program name: Chats
Description: Client
Date: 06.03.2022

Protocol:

-------------------------------------------- Without Files -------------------------------------------------------------
                                            *** Part 1 ***
sends data len with padding and username with padding, FOR EXAMPLE:
if the len is 82 and the username is 'Omer' it will send '290             ############Omer'
                                            *** Part 2 ***
after this it sends the data with separation between fields & fields description & number of fields & cmd but every
char of the message is converted to ascii value because if the message is in hebrew it doesn't work well if you just
send it like that. EXAMPLE:
this msg: "send_msg#@?#3#@?#user_name#@?#chat_with#@?#msg#@?#the username#@?#Someone#@?#hello" will be converted to
"115,101,110,100,95,109,115,103,35,64,63,35,51,35,64,63,35,117,115,101,114,95,110,97,109,101,35,64,63,35,99,104,97,116,"
"95,119,105,116,104,35,64,63,35,109,115,103,35,64,63,35,116,104,101,32,117,115,101,114,110,97,109,101,35,64,63,35,83,"
"111,109,101,111,110,101,35,64,63,35,104,101,108,108,111,"
-------------------------------------------- With Files -------------------------------------------------------------
every thing is the same, except there will be a field that says the length of the file as well as some other fields.
and the file will be added at the end of the message
EXAMPLE:
upload_file#@?#4#@?#user_name#@?#other_username#@?#file_size#@?#filename.?#@?#     המשך שורה הבאה
the username#@?#someone#@?#size of file#@?#the type of file(.exe .txt ...)#@?#the file it self
and this will be converted to the ascii value as well, except from the file itself.
"""


# ** site-packages folder is included in this zip file in case something doesn't work well **
import logging
import sys
import multiprocessing
import os
import pyaudio
import pyperclip
import shutil
import socket
import time
import wave
from datetime import datetime
from PIL import Image as ImagePIL  # pip install Pillow not PIL
from PIL.ImageOps import contain
from PIL import ImageTk as ImageTkPIL
from playsound import playsound  # playsound version 1.2.2 only !! (pip install playsound==1.2.2)
from threading import Thread
from tkinter import *  # pip install tkinter
from tkinter import filedialog
from tkinter import scrolledtext


# logging
LOG_FORMAT = "%(levelname)s | %(asctime)s | %(processName)s | %(message)s"
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = LOG_DIR + "/Chats-Client.log"

# constants
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
                         "'1234567890_-"
BUTTON_STATE = {"normal": NORMAL, "active": ACTIVE, "disabled": DISABLED}
PHOTO_PREVIEW_FILE_EXTENSIONS = [".png", ".jpeg", ".ico", ".jpg", ".tif"]
AUDIO_FILE_EXTENSIONS = [".mp3", ".wav", ".m4a", ".mp2"]

# globals
chat_scrolledtext = []
chat_data = []
chat_name = []
chat_button = []
all_chats_text = []
all_chats_button = []
playing_file_path = None
playing_thread = None
playing_button = None
global user_name, msg_box, my_socket, current_chat_text, main_window, gui_status, home_chat, \
    chat_buttons, current_chat, search_username, current_chat_name, stop_rec, record_button


class MainWindow:
    """
    class for creating a window
    """

    def __init__(self, size="980x520", state="zoomed", min_size=(980, 520), window_name="#", max_size=None,
                 columnconfig=True, rowconfig=True):
        global user_name
        if window_name == "#":
            window_name = user_name
        # Create Window
        self.root = Tk()
        # Configure Window
        self.root.title("Chats - " + window_name)  # title of window
        self.root.iconbitmap(resource_path("chats.ico"))  # icon of window
        self.root.config(bg="#050c29")  # background color of window
        self.root.minsize(min_size[0], min_size[1])  # minimum size of window
        if max_size is not None:
            self.root.maxsize(max_size[0], max_size[1])  # max size of window
        self.root.geometry(size)  # default size of window
        if state == "zoomed":
            self.root.state(state)  # open window in full-screen windowed
        # Rows and Columns configuration
        if columnconfig:
            self.root.columnconfigure(2, weight=1)
        if rowconfig:
            self.root.rowconfigure((1, 2), weight=1)
        self.widgets = []

    def get_root(self):
        """
        :return: the window
        :rtype: tkinter.Tk
        """
        return self.root

    def add_widget(self, widget, row, column, rowspan=1, columnspan=1, sticky=''):
        """
        adds a widget
        :param widget: the widget
        :param row: the row to add the widget
        :param column: the column to add the widget
        :param rowspan: the amount of rows the widget will take
        :param columnspan: the amount of columns the widget will take
        :param sticky: if the widget should resize with the window, and if so to which direction (n e w s)
        :type row: int
        :type column: int
        :type rowspan: int
        :type columnspan: int
        :type sticky: str
        """
        self.widgets.append(widget)
        self.widgets[self.widgets.index(widget)].grid(row=row, column=column, rowspan=rowspan,
                                                      columnspan=columnspan, sticky=sticky)

    def remove_widget(self, widget):
        """
        removes a widget from the window
        :param widget: the widget to remove
        """
        self.widgets[self.widgets.index(widget)].grid_remove()


class ChatButtons:
    """
    class for the scrolled text window that contains all the user chat buttons
    """

    def __init__(self):
        global main_window
        self.buttons = scrolledtext.ScrolledText(main_window.get_root())  # text window for all the chats buttons
        self.buttons.config(state=DISABLED, width=42, borderwidth=5, height=27, bg="#202021", cursor="arrow")
        self.buttons.bind('<MouseWheel>', mouse_wheel_buttons)

    def get_chatbuttons(self):
        """
        :return: the scrolledtext containing the chat buttons
        :rtype: tkinter.scrolledtext.ScrolledText
        """
        return self.buttons

    def add_button(self, button):
        """
        adds a button to the scrolled text window
        :param button: the button
        :type button: tkinter.Button
        """
        self.buttons.insert("end", "\r\n")
        self.buttons.window_create("end", window=button)

    def remove_all_buttons(self):
        """
        destroys all the widget in the scrolled text window
        """
        for widget in self.buttons.winfo_children():
            widget.destroy()


class EntryBox:
    """
    class for entry boxes
    """

    def __init__(self, master, w=1, borderwidth=1, bg="#ffffff", fg="#000000", font=("helvetica", 16)):
        self.entry = Entry(master, width=w, borderwidth=borderwidth, bg=bg, fg=fg, font=font)

    def get_entry(self):
        """
        :return: the entry
        :rtype: tkinter.Entry
        """
        return self.entry

    def insert(self, text):
        """
        inserts text to the entry box
        :param text: the text to add
        :type text: str
        """
        self.entry.insert("end", text)

    def clear(self):
        """
        clears the entry box
        """
        self.entry.delete(0, END)

    def get_text(self):
        """
        :return: the text in the entry box
        :rtype: str
        """
        return self.entry.get()

    def bind(self, button, func):
        """
        binds the entry box with a button and a function
        :param button: the button that you want to bind to the entry box
        :param func: the function to call
        :type button: str
        """
        self.entry.bind(button, func)


class Buttonn:
    """
    class for buttons
    """

    def __init__(self, master, w=None, h=None, borderwidth=1, bg="#ffffff", fg="#000000", font=("helvetica", 16),
                 text="", command=None, state=NORMAL, image=None, justify="left", name=None):
        """
        :type justify: literal
        """
        if w is None and h is None:
            self.button = Button(master, borderwidth=borderwidth, fg=fg, font=font, text=text, compound="top",
                                 command=command, bg=bg, state=state, image=image, justify=justify)
        else:
            self.button = Button(master, width=w, height=h, borderwidth=borderwidth, fg=fg, font=font, text=text,
                                 command=command, bg=bg, state=state, image=image, justify=justify, compound="top")
        self.name = name

    def get_button(self):
        """
        :return: the button
        :rtype: tkinter.Button
        """
        return self.button

    def get_button_text(self):
        """
        :return: the text on the button
        :rtype: str
        """
        txt = self.button["text"]
        space = False
        while "(" in txt:  # remove the amount of unread messages 'name (x)'
            space = True
            txt = txt[:-1]
        if space:  # remove the space that is left after the amount of unread messages 'name (x)'
            txt = txt[:-1]
        return txt

    def change_text(self, text):
        """
        changes the text on the button
        :param text: the text to change to
        :type text: str
        """
        state = BUTTON_STATE[self.button["state"]]
        self.button.config(state=ACTIVE, text=text)
        self.button.config(state=state)

    def change_color(self, bg="", fg=""):
        """
        changes the background color and/or the foreground color
        :param bg: the background color green/white/blue... or code (#ffffff...)
        :param fg: the foreground color green/white/blue... or code (#ffffff...)
        :type bg: str
        :type fg: str
        """
        state = BUTTON_STATE[self.button["state"]]  # save current state of button
        if bg != "" and fg != "":
            self.button.config(state=ACTIVE, background=bg, foreground=fg)
        elif fg == "" and bg != "":
            self.button.config(state=ACTIVE, background=bg)
        elif bg == "":
            self.button.config(state=ACTIVE, foreground=fg)
        self.button.config(state=state)  # return to the state the button was at the beginning

    def change_state(self, state):
        """
        changes the state of the button
        :param state: the state to change the button to
        :type state: literal
        """
        self.button.config(state=state)

    def change_command(self, new_command):
        """
        changes the command of the button
        """
        self.button.config(command=new_command)

    def new_messages(self):
        """ changes the button color to green to notify the user that there is a new message"""
        self.button.config(background="#08c928")

    def change_name(self, name):
        """
        changes the name of the button (just a variable I added, so you can have
        text that belongs to a button without it being displayed
        :param name: the text that won't be displayed
        :type name: str
        """
        self.name = name

    def get_name(self):
        """
        :return: the name of the button
        :rtype: str
        """
        return self.name

    def pack(self):
        """ Packs A Widget To The Screen
        (it's either this method or grid, can't to both on the same window)"""
        self.button.pack(expand=True)


class Labell:
    """
    class for labels
    """

    def __init__(self, master, text, bg="#ffffd0", font=("helvetica", 16), justify="left", fg="black", h=0):
        """
        :type justify: literal
        """
        if text[0] == " ":
            text = text[1:]
        if "#@##@!?#This Message Was Deleted." in text:
            text = "This Message Was Deleted."
            bg = "gray"
        if h != 0:
            self.label = Label(master, text=text, bg=bg, font=font, justify=justify, fg=fg, height=h)
        else:
            self.label = Label(master, text=text, bg=bg, font=font, justify=justify, fg=fg)

    def get_label(self):
        """
        :return: the label
        :rtype: tkinter.Label
        """
        return self.label

    def get_label_text(self):
        """
        :return: the text on the label
        :rtype: str
        """
        return self.label["text"]

    def bind(self, button, func):
        """
        binds the label with a button and a function
        :param button: the button that you want to bind to the label
        :param func: the function to call when the button is triggered while the mouse pointer is on the label
        :type button: str
        """
        self.label.bind(button, func)

    def unbind(self, button):
        """
        Unbinds all the binds to the given button
        :param button: the button to unbind
        :type button: str (example: <Button-1>)
        """
        self.label.unbind(button)

    def change_text(self, text):
        """
        changes the text on the label
        :param text: the text to be displyed
        :type text: str
        """
        self.label.config(text=text)

    def change_color(self, bg, fg):
        """
        changes the bg and/or fg color of the label
        :param bg: the background color green/white/blue... or code (#ffffff...)
        :param fg: the foreground color green/white/blue... or code (#ffffff...)
        :type bg: str
        :type fg: str
        """
        if bg != "" and fg != "":
            self.label.config(background=bg, foreground=fg)
        elif fg == "" and bg != "":
            self.label.config(background=bg)
        elif bg == "":
            self.label.config(foreground=fg)


class ChatWindow:
    """
    class for scrolled text window (the chats)
    """

    def __init__(self, master, state=DISABLED, bg="#282829", borderwidth=0, w=999, h=999, font=('helvetica', '16')):
        self.txt = scrolledtext.ScrolledText(master)
        self.txt.configure(state=state, bg=bg, borderwidth=borderwidth, width=w, height=h, font=font, cursor="arrow")
        self.txt.bind('<MouseWheel>', mouse_wheel_texts)  # enable to scroll with mouse wheel
        self.txt.tag_configure("tag-left", justify="left")
        self.txt.tag_configure("tag-right", justify="right")
        self.txt.tag_configure("tag-center", justify="center")
        self.txt.tag_configure("tag-center-green", justify="center", foreground="#08c928")
        self.txt.tag_configure("tag-chats", justify="center", foreground="#62C6D7", font=('helvetica', '24'))
        self.txt.yview_pickplace("end")

    def get_chatwindow(self):
        """
        :return: the scrolledtext chat window
        :rtype: tkinter.scrolledtext.ScrolledText
        """
        return self.txt

    def change_state(self, state):
        """
        changes the state of the scrolled text window
        :param state: the state to change the window to
        :type state: literal
        """
        self.txt.config(state=state)

    def insert(self, text, tag=""):
        """
        inserts text to the scrolled text window
        :param text: the text to insert
        :param tag: the tag of the text (left right or center)
        :type text: str
        :type tag: str
        """
        if tag != "":
            self.txt.insert("end", text, tag)

    def home_chat(self):
        """
        Adds a pattern to the home chat
        """
        self.change_state(NORMAL)
        for i in range(0, 6):
            if i != 3:
                self.insert("Chats     Chats     Chats     Chats     Chats     Chats     Chats     Chats     Chats     "
                            "Chats     Chats     Chats     \n\n",
                            tag="tag-chats")
                if i != 2:
                    self.insert("     Chats     Chats     Chats     Chats     Chats     Chats     Chats     Chats     "
                                "Chats     Chats     Chats     Chats\n\n",
                                tag="tag-chats")
                else:
                    self.insert("Chats     Chats     Chats     Chats ------------------------------------------- "
                                "Chats     Chats     Chats     Chats\n\n",
                                tag="tag-chats")
            else:
                self.insert("Chats     Chats     Chats     Chats  |            Welcome To Chats           |  Chats     "
                            "Chats     Chats     Chats  \n\n",
                            tag="tag-chats")
                self.insert("Chats     Chats     Chats     Chats ------------------------------------------- Chats"
                            "     Chats     Chats     Chats\n\n",
                            tag="tag-chats")
        self.insert("Chats     Chats     Chats     Chats     Chats     Chats     Chats     Chats     Chats     "
                    "Chats     Chats     Chats     ",
                    tag="tag-chats")
        self.change_state(DISABLED)

    def insert_label_right(self, text, copy_text, index):
        """
        inserts a label on the right side
        :param text: the text on the label
        :param copy_text: the text that will be copied from label
        :param index: the index of the msg in the chat
        :type text: str
        :type copy_text: str
        :type index: int
        """
        label = Labell(self.txt, text)
        label.bind("<Button-3>",
                   lambda event, type="from user", copy_text=copy_text, index=index:
                   message_options_(type, copy_text, index, event, label))
        self.change_state(NORMAL)
        self.insert("\n ", tag="tag-right")
        self.txt.window_create("end", window=label.get_label())
        self.insert("                                    \n", tag="tag-left")
        self.change_state(DISABLED)

    def insert_label_left(self, text, copy_text, index):
        """
        inserts a label on the left side
        :param text: the text on the label
        :param copy_text: the text that will be copied from label
        :param index: the index of the msg in the chat
        :type text: str
        :type copy_text: str
        :type index: int
        """
        label = Labell(self.txt, text, bg="#d0ffff")
        label.bind("<Button-3>",
                   lambda event, type="to user", copy_text=copy_text, index=index:
                   message_options_(type, copy_text, index, event, label))
        self.change_state(NORMAL)
        self.insert("\n                                    ", tag="tag-left")
        self.txt.window_create("end", window=label.get_label())
        self.insert("\n", tag="tag-left")
        self.change_state(DISABLED)

    def unread_messages(self, line, amount):
        """
        inserts a message to let the user know where the new messages start
        :param line: the line that the scrolled text window will wait at
        :param amount: the amount of unread messages
        :type line: float
        :type amount: int
        """
        self.change_state(NORMAL)
        if amount == 1:
            self.insert("\n--------------------------------------- "
                        "%d Unread Message"
                        " ---------------------------------------\n" % amount, tag="tag-center-green")
        else:
            self.insert("\n--------------------------------------- "
                        "%d Unread Messages"
                        " ---------------------------------------\n" % amount, tag="tag-center-green")
        self.go_to_specific_line(line)
        self.change_state(DISABLED)

    def insert_button_right(self, text, file):
        """
        inserts a button on the right side
        if the file is in PHOTO_PREVIEW_FILE_EXTENSIONS it will display an image preview
        if the file is in AUDIO_FILE_EXTENSIONS when you'll click the button it will play the audio file
        :param text: the text on the button
        :param file: the name of the file that will be executed if the button gets pressed
        :type text: str
        :type file: str
        """
        global user_name, playing_thread, playing_file_path
        # check of file is an image (and a supported one)
        if "." + file.split(".")[-1] in PHOTO_PREVIEW_FILE_EXTENSIONS:
            # get the full path of the photo
            location = "\\".join(os.path.abspath(__file__).split("\\")[:-1]) + "\\" + user_name + "\\" + file
            img = contain(ImagePIL.open(location), (480, 360))  # resize to a max of 480x360
            img = ImageTkPIL.PhotoImage(img)
        else:
            img = None
        if file.endswith(".ico"):  # white background for .ico files else green
            bg = "#ffffff"
        else:
            bg = "#0e7a0c"
        if "." + file.split(".")[-1] in AUDIO_FILE_EXTENSIONS:  # check of file is an audio file (and a supported one)
            location = "\\".join(os.path.abspath(__file__).split("\\")[:-1]) + "\\" + user_name + "\\" + file
            if playing_file_path == location:
                text += "\nPress To Stop"
                count = text.count("\n") + 1
                button = Buttonn(self.txt, text=text, bg=bg, font=("helvetica", 16), justify="left",
                                 w=30, h=count, name=text)
                button.change_command(lambda: terminate_and_restore_button(playing_thread, button, location))
            else:
                text += "\nPress To Play"
                count = text.count("\n") + 1
                button = Buttonn(self.txt, text=text, bg=bg, font=("helvetica", 16), justify="left",
                                 w=30, h=count, name=text)
                button.change_command(lambda: play_audio_thread(location, button))
        elif "\n" in text:  # with seen message or without?
            if img is None:  # is the file an image? if so photo preview
                button = Buttonn(self.txt, text=text, bg=bg, font=("helvetica", 16), justify="left", w=30, h=2,
                                 command=lambda: display_file(file))
            else:
                text = "Press To Open\n" + text.split("\n")[1]
                button = Buttonn(self.txt, text=text, font=("helvetica", 10), justify="center", bg=bg,
                                 command=lambda: display_file(file), image=img)
                button.get_button().photo = img
        else:
            if img is None:  # is the file an image? if so photo preview
                button = Buttonn(self.txt, text=text, bg=bg, font=("helvetica", 16), justify="left", w=30,
                                 command=lambda: display_file(file))
            else:
                text = "Press To Open"
                button = Buttonn(self.txt, text=text, font=("helvetica", 10), justify="center", bg=bg,
                                 command=lambda: display_file(file), image=img)
                button.get_button().photo = img
        self.change_state(NORMAL)
        self.insert("\n ", tag="tag-right")
        self.txt.window_create("end", window=button.get_button())
        self.insert("                                    \n", tag="tag-left")
        self.change_state(DISABLED)

    def insert_button_left(self, text, file):
        """
        inserts a button on the left side
        if the file is in PHOTO_PREVIEW_FILE_EXTENSIONS it will display an image preview
        if the file is in AUDIO_FILE_EXTENSIONS when you'll click the button it will play the audio file
        :param text: the text on the button
        :param file: the name of the file that will be executed if the button gets pressed
        :type text: str
        :type file: str
        """
        global user_name
        # check of file is an image (and a supported one)
        if "." + file.split(".")[-1] in PHOTO_PREVIEW_FILE_EXTENSIONS:
            # get the full path of the photo
            location = "\\".join(os.path.abspath(__file__).split("\\")[:-1]) + "\\" + user_name + "\\" + file
            img = contain(ImagePIL.open(location), (480, 360))  # resize to a max of 480x360
            img = ImageTkPIL.PhotoImage(img)
        else:
            img = None
        if file.endswith(".ico"):  # white background for .ico files else green
            bg = "#ffffff"
        else:
            bg = "#0e7a0c"
        if "." + file.split(".")[-1] in AUDIO_FILE_EXTENSIONS:  # check of file is an audio file (and a supported one)
            location = "\\".join(os.path.abspath(__file__).split("\\")[:-1]) + "\\" + user_name + "\\" + file
            if playing_file_path == location:
                text += "\nPress To Stop"
                button = Buttonn(self.txt, text=text, bg=bg, font=("helvetica", 16), justify="left",
                                 w=30, h=2, name=text)
                button.change_command(lambda: terminate_and_restore_button(playing_thread, button, location))
            else:
                text += "\nPress To Play"
                button = Buttonn(self.txt, text=text, bg=bg, font=("helvetica", 16), justify="left",
                                 w=30, h=2, name=text)
                button.change_command(lambda: play_audio_thread(location, button))
        elif img is None:  # is the file an image? if so photo preview
            button = Buttonn(self.txt, text=text, bg=bg, font=("helvetica", 16), justify="left", w=30, h=1,
                             command=lambda: display_file(file))
        else:
            text = "Press To Open"
            button = Buttonn(self.txt, text=text, bg=bg, font=("helvetica", 10), justify="left",
                             command=lambda: display_file(file), image=img)
            button.get_button().photo = img
        self.change_state(NORMAL)
        self.insert("\n                                    ", tag="tag-left")
        self.txt.window_create("end", window=button.get_button())
        self.insert("\n", tag="tag-left")
        self.change_state(DISABLED)

    def go_to_end(self):
        """" moves the view to the end (the most recent message) """
        self.txt.yview_pickplace("end")

    def go_to_specific_line(self, line):
        """
        moves the view to a specific line
        :param line: the line to move to
        :type line: float
        """
        self.txt.see(line)

    def scroll(self):
        """ changes the view """
        self.txt.yview_scroll(0.1, "pixels")


def resource_path(relative_path):
    """ return the path to a resource """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def mouse_wheel_texts(event):
    """ scroll with mouse wheel """
    global current_chat_text
    if event.delta == -120:
        current_chat_text.scroll()
    if event.delta == 120:
        current_chat_text.scroll()


def mouse_wheel_buttons(event=None):
    """
    scroll with mouse wheel
    :param event: because this function is called from a button press it can send this func an event
    """
    global chat_buttons
    if event.delta == -120:
        chat_buttons.get_chatbuttons().yview_scroll(1, "units")
    if event.delta == 120:
        chat_buttons.get_chatbuttons().yview_scroll(-1, "units")


def search_delete_on_click(event=None):
    """"
    deletes the text in the entry box of user search when it's clicked on
    :param event: because this function is called from a button press it can send this func an event
    """
    global search_username
    text = search_username.get_text()
    if text == "" or text == "Start a new chat" or text == "Error" or text == "Invalid User Name" or \
            text == "Please Type A User Name" or text == "You Can't Start A Chat With Yourself" or \
            text == "Username Doesn't Exists" or text == "Chat Already Exists":
        search_username.clear()
        search_username.insert('')


def enter_key(event=None):
    """
    allows to press on the enter key to send a message
    :param event: because this function is called from a button press it can send this func an event
    """
    global user_name, msg_box, current_chat
    if len(event.char) > 0 and ord(event.char) == 13:
        send_message(current_chat.get_label_text(), msg_box.get_entry())


def enter_key_search_user(event=None):
    """
    allows to press on the enter key to search a user
    :param event: because this function is called from a button press it can send this func an event
    """
    global search_username, user_name
    if len(event.char) > 0 and ord(event.char) == 13:
        new_chat(search_username, user_name)


def display_file(file_name, event=None):
    """"
    executes a file
    :param file_name: the path to the file
    :param event: because this function is called from a button press it can send this func an event
    :type file_name: str
    """
    global user_name
    location = os.path.abspath(__file__).split("\\")
    del location[-1]
    location = "\\".join(location)
    location += "\\" + user_name + "\\" + file_name
    if os.path.isfile(location):
        try:
            os.startfile(location)
        except os.error as err:
            logging.warning(str(err) + " (display_file)")


def play_audio_thread(filepath, button):
    """
    Creates a thread that plays the audio file and changes the button text
    :param filepath: the path to the audio file
    :param button: the button that got pressed
    :type filepath: str
    :type button: Buttonn
    """
    global playing_thread, playing_file_path, playing_button
    if playing_file_path is not None:  # if there is something playing right now it will terminate it
        terminate_and_restore_button(playing_thread, playing_button, playing_file_path)
    play_ = multiprocessing.Process(target=playsound, args=(filepath,), daemon=True)
    play_.start()
    playing_thread = play_
    playing_file_path = filepath
    playing_button = button
    text = button.get_name()
    if text is not None:
        text = "\n".join(text.split("\n")[:-1]) + "\nPress To Stop"
        button.change_text(text)
        button.change_name(text)
    else:
        button.change_text("Stop")
    button.change_command(lambda: terminate_and_restore_button(play_, button, filepath))
    check_if_finished = Thread(target=check_if_process_alive, args=(play_, button, filepath,), daemon=True)
    check_if_finished.start()


def check_if_process_alive(play_, button, filepath):
    """
    Checks if the audio file is still being played, if not shuts the thread
    :param play_: the thread that the file is being played from
    :param button: the button that got pressed
    :param filepath: the path to the audio file
    :type play_: multiprocessing.Process
    :type button: Buttonn
    :type filepath: str
    """
    while True:
        if not play_.is_alive():
            terminate_and_restore_button(play_, button, filepath)
            break


def terminate_and_restore_button(play_, button, filepath):
    """
    Terminates the thread of the audio file
    Restores button
    :param play_: the thread that the file is being played from
    :param button: the button that got pressed
    :param filepath: the path to the audio file
    :type play_: multiprocessing.Process
    :type button: Buttonn
    :type filepath: str
    """
    global playing_thread, playing_file_path, playing_button
    play_.terminate()
    if playing_button == button and playing_thread == play_ and playing_file_path == filepath:
        playing_thread = None
        playing_file_path = None
        playing_button = None
    text = button.get_name()
    if text is not None:
        text = "\n".join(text.split("\n")[:-1]) + "\nPress To Play"
        button.change_text(text)
        button.change_name(text)
    else:
        button.change_text("Play")
    button.change_command(lambda: play_audio_thread(filepath,  button))


def stop_recording():
    """ Changes the global variable stop_rec to False """
    global stop_rec
    stop_rec = True


def record_():
    """ Creates a Thread to record """
    global stop_rec, record_button, current_chat_name
    if current_chat_name != "Home":
        stop_rec = False
        rec_ = Thread(target=record, daemon=True)
        rec_.start()
        record_button.change_command(stop_recording)
        record_button.change_text("Stop Recording")


def record():
    """
    Records Audio
    Saves it to a file named temp.wav in the user folder
    calls the upload_file__ function to send the file to the other user
    """
    global stop_rec, record_button, user_name
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
    frames = []
    while not stop_rec:
        data = stream.read(1024)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    audio.terminate()
    sound_file = wave.open(r"%s\temp.wav" % user_name, "wb")
    sound_file.setnchannels(1)
    sound_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
    sound_file.setframerate(44100)
    sound_file.writeframes(b''.join(frames))
    sound_file.close()
    record_button.change_command(record_)
    record_button.change_text("Record")
    options_thread = Thread(target=recording_options, daemon=True)
    options_thread.start()


def delete_file_close_window(filepath, root):
    """
    deletes the voice recording and closes the voice recording options window
    :param filepath: the path of the voice recording file
    :param root: the root of the options window
    :type filepath: str
    :type root: tkinter.Tk
    """
    os.remove(filepath)
    root.destroy()


def recording_options():
    """
    after recording this function will be called to open a window with 3 options
    1) play - plays the voice recording
    2) delete - deletes the voice recording (doesn't send it)
    3) send - send the voice recording
    """
    global main_window
    color = "#ffffd0"
    size = 120
    window_x = main_window.get_root().winfo_screenwidth() / 2
    window_y = main_window.get_root().winfo_screenheight() / 2
    options_window = MainWindow(window_name="Options", max_size=(250, size), min_size=(250, size), state="",
                                size="250x%d+%d+%d" % (size, window_x, window_y), columnconfig=False, rowconfig=False)
    root = options_window.get_root()
    play = Buttonn(root, text="Play", bg=color, w=21)
    play.change_command(lambda: play_audio_thread(r"%s\temp.wav" % user_name, play))
    options_window.add_widget(play.get_button(), row=0, column=0, sticky="news")
    delete = Buttonn(root, text="Delete", bg=color,
                     command=lambda: delete_file_close_window(r"%s\temp.wav" % user_name, root))
    options_window.add_widget(delete.get_button(), row=1, column=0, sticky="news")
    send = Buttonn(root, text="Send", bg=color,
                   command=lambda: upload_file__(current_chat_name, filename=r"%s\temp.wav" % user_name, root=root))
    options_window.add_widget(send.get_button(), row=2, column=0, sticky="news")
    root.mainloop()
    # if user didn't press anything and closed the window the recording file still exist so this deletes it
    if os.path.isfile(r"%s\temp.wav" % user_name):
        os.remove(r"%s\temp.wav" % user_name)


def copy2clipboard(text, root):
    """
    copies the text to the clipboard
    :param text: the text that will be copied
    :param root: the root of the window of the message options
    :type text: str
    :type root: tkinter.Tk
    """
    pyperclip.copy(text)
    root.destroy()


def delete(other_username, index, root):
    """
    deletes the msg in the chat with other_username at index for the user only
    :param other_username: the chat that the msg is from
    :param index: the index of the msg in the chat
    :param root: the root of the window of the message options
    :type other_username: str
    :type index: int
    :type root: tkinter.Tk
    """
    global user_name
    assemble_protocol_and_send(cmd="delete_for_me", number_of_fields=3,
                               fields=["user_name", "other_username", "index"],
                               data_of_fields=[user_name, other_username, str(index)])
    root.destroy()


def delete_for_all(other_username, index, root):
    """
    deletes the msg in the chat with other_username at index for the user and for the other user
    :param other_username: the chat that the msg is from
    :param index: the index of the msg in the chat
    :param root: the root of the window of the message options
    :type other_username: str
    :type index: int
    :type root: tkinter.Tk
    """
    global user_name
    assemble_protocol_and_send(cmd="delete_for_all", number_of_fields=3,
                               fields=["user_name", "other_username", "index"],
                               data_of_fields=[user_name, other_username, str(index)])
    root.destroy()


def message_options_(message_type, copy_text, index, event, label):
    """
    opens a thread for message_options
    :param message_type: message from user or message to user
    :param copy_text: the text that will be copied from the label if the user will press the copy button
    :param index: the index of the msg in the chat
    :param event: the event that called this func
    :param label: the label that got pressed
    :type message_type: str ('from user' or 'to user')
    :type copy_text: str
    :type index: int
    :type label: Labell
    """
    label.unbind("<Button-3>")
    options_thread = Thread(target=message_options, args=(message_type, copy_text, index, event, label,), daemon=True)
    options_thread.start()


def message_options(message_type, copy_text, index, event, label):
    """
    Opens a window that shows 2 or 3 option
    (copy, delete for me, and if the msg is from the user there is also delete for everyone
    :param message_type: message from user or message to user
    :param copy_text: the text that will be copied from the label if the user will press the copy button
    :param index: the index of the msg in the chat
    :param event: the event that called this func
    :param label: the label that got pressed
    :type message_type: str ('from user' or 'to user')
    :type copy_text: str
    :type index: int
    :type label: Labell
    """
    global user_name, current_chat_name
    if message_type == "from user":
        color = "#ffffd0"
        size = 120
    else:
        color = "#d0ffff"
        size = 80
    window_x = event.x + label.get_label().winfo_x()
    window_y = event.y + label.get_label().winfo_y()
    options_window = MainWindow(window_name="Options", max_size=(250, size), min_size=(250, size), state="",
                                size="250x%d+%d+%d" % (size, window_x, window_y), columnconfig=False, rowconfig=False)
    root = options_window.get_root()
    copy = Buttonn(root, text="Copy", bg=color, command=lambda: copy2clipboard(copy_text, root), w=21)
    options_window.add_widget(copy.get_button(), row=0, column=0, sticky="news")
    delete_for_me = Buttonn(root, text="Delete For Me", bg=color,
                            command=lambda: delete(current_chat_name, index, root))
    options_window.add_widget(delete_for_me.get_button(), row=1, column=0, sticky="news")
    if message_type == "from user":
        delete_for_everyone = Buttonn(root, text="Delete For Everyone", bg=color,
                                      command=lambda: delete_for_all(current_chat_name, index, root))
        options_window.add_widget(delete_for_everyone.get_button(), row=2, column=0, sticky="news")
    root.mainloop()
    label.bind("<Button-3>",
               lambda event, type=message_type, copy_text=copy_text, index=index, label=label:
               message_options_(type, copy_text, index, event, label))


def update_gui():
    """ updates the gui - rebuilds all the chat buttons and all the chat windows & titles """
    global user_name, msg_box, current_chat_text, main_window, chat_buttons, \
        current_chat, search_username, current_chat_name, all_chats_button, all_chats_text
    chat_buttons.remove_all_buttons()
    all_chats_button = []
    if current_chat_name != "Home":
        main_window.remove_widget(current_chat_text.get_chatwindow())
    else:
        if current_chat_text != home_chat:
            main_window.remove_widget(current_chat_text.get_chatwindow())
            current_chat.change_text("Home")
            current_chat_text = home_chat
            main_window.add_widget(home_chat.get_chatwindow(), row=1, column=2, sticky='news', columnspan=2)
    all_chats_text = []
    chats_name = []
    chats_data = []
    for chat_name in os.listdir(user_name + "\\"):
        if chat_name.endswith(".txt") and any(char in USERNAME_ALLOWED_CHARS for char in chat_name[:-4]) \
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
    if "last_seen" in chats_name:
        del chats_data[chats_name.index("last_seen")]
        chats_name.remove("last_seen")
    new_messages = ""
    amount = 0
    for data in chats_data:
        sctxt = ChatWindow(main_window.get_root())
        msgs = data.split("\n")
        del msgs[-1]
        while "" in msgs:
            msgs.remove("")
        unread_messages = False
        for msg in msgs:
            # this means that this msg was deleted for the user only (delete for me) so continue to skip this msg
            if "#@##@!?#Don'tDisplay" in msg:
                continue
            index = msgs.index(msg)
            if r"*\n*" in msg:
                msg = "\n".join(msg.split(r"*\n*"))
            if msg.startswith(user_name + ": "):  # insert all text of the user
                if "#@??##" not in msg:
                    msg = msg[len(user_name) + 2:]
                    seen = ""
                    if "#@!#(seen at " in msg:
                        seen = "\n" + msg[-1:-28:-1][::-1]
                        msg = msg[:-31]
                    copy_text = msg
                    if len(msg) > 50:  # if msg is more than 50 chars it will add \n about every 50 chars
                        words = msg.split(" ")
                        for i in range(0, len(words)):
                            word = words[i]
                            # if there is a word that is longer then 50 chars (spam msg) it will add \n every 50 chars
                            if len(word) > 50:
                                msg = ""
                                count = 0
                                for char in word:
                                    if count == 50:
                                        msg += "\n" + char
                                        count = 0
                                    else:
                                        msg += char
                                    count += 1
                                words[i] = msg
                        current_line = 0
                        msg = ""
                        for word in words:  # assembles the msg
                            if current_line + len(word) < 50:
                                msg += word + " "
                                current_line += len(word) + 1
                            else:
                                if len(msg) > 1:
                                    msg += "\n" + word + " "
                                else:
                                    msg += word + " "
                                current_line = len(word) + 1
                    msg += seen
                    sctxt.insert_label_right(msg, copy_text, index)
                else:
                    file_name = msg.split("#@??##")[-1]
                    seen = ""
                    if "#@!#(seen at " in file_name:
                        seen = "\n" + file_name.split("#@!#")[1]
                        file_name = file_name.split("#@!#")[0]
                    sctxt.insert_button_right(text=file_name + seen, file=file_name)
            else:  # insert all texts of the other user
                if "#@??##" not in msg and "#@?!?##*" not in msg:
                    msg = msg.split(":")
                    del msg[0]
                    msg = ":".join(msg)
                    copy_text = msg
                    if len(msg) > 50:  # if msg is more than 50 chars it will add \n about every 50 chars
                        words = msg.split(" ")
                        for i in range(0, len(words)):
                            word = words[i]
                            # if there is a word that is longer then 50 chars (spam msg) it will add \n every 50 chars
                            if len(word) > 50:
                                msg = ""
                                count = 0
                                for char in word:
                                    if count == 50:
                                        msg += "\n" + char
                                        count = 0
                                    else:
                                        msg += char
                                    count += 1
                                words[i] = msg
                        current_line = 0
                        msg = ""
                        for word in words:  # assembles the msg
                            if current_line + len(word) < 50:
                                msg += word + " "
                                current_line += len(word) + 1
                            else:
                                if len(msg) > 1:
                                    msg += "\n" + word + " "
                                else:
                                    msg += word + " "
                                current_line = len(word) + 1
                    sctxt.insert_label_left(msg, copy_text, index)
                elif "#@?!?##*" in msg:
                    # ------------- Unread Messages -------------
                    new_messages = chats_data.index(data)
                    unread_messages = True
                    line = msgs.index(msg)
                    amount_of_new_messages = len(msgs) - line - 1
                    amount = amount_of_new_messages
                    if 4 < line < len(msgs) - 6:
                        line -= 4
                    sctxt.unread_messages(line * 2.0, amount_of_new_messages)
                elif "#@??##" in msg:
                    file_name = msg.split("#@??##")[-1]
                    sctxt.insert_button_left(text=file_name, file=file_name)
        if not unread_messages:
            sctxt.go_to_end()
        all_chats_text.append(sctxt)
        if chats_name[chats_data.index(data)] == current_chat_name:
            main_window.add_widget(sctxt.get_chatwindow(), row=1, column=2, sticky='news', columnspan=2)
            # change chat title
            file = open(user_name + "\\connected_users.txt", encoding='utf-8')
            connected_users = file.read() + "#@!#"
            file = open(user_name + "\\last_seen.txt", encoding='utf-8')
            last_seen = file.read()
            file.close()
            t = current_chat_name
            if t + "#@!#" in connected_users:
                t += " (Online)"
                current_chat.change_color(bg="#00b52a", fg="black")
            elif t + " = " in last_seen:
                last_seen = last_seen.split("#@!#")
                for user in last_seen:
                    if user.startswith(t + " = "):
                        last_seen_with_date_or_without = datetime.now().strftime("%m/%d/%Y, %H:%M")
                        if user.split(" = ")[-1].startswith(last_seen_with_date_or_without[:-5]):
                            seen_time = user.split(" = ")[-1][-5:]
                        else:
                            seen_time = user.split(" = ")[-1]
                        t += "\nLast Seen At " + seen_time
                        break
                current_chat.change_color(bg="#282829", fg="white")
            else:
                current_chat.change_color(bg="#282829", fg="white")
            main_window.remove_widget(current_chat_text.get_chatwindow())
            current_chat.change_text(t)
            current_chat_text = sctxt
    for i in range(0, len(chats_name)):
        def clicked(x=i):
            """ if a chat button is clicked it will display the chat window
            (must be inside the loop, or it won't work)
            """
            global main_window, current_chat_text, current_chat_name, user_name
            # Remove current text from the screen
            main_window.remove_widget(current_chat_text.get_chatwindow())
            # Places the chosen text on the screen
            ct = all_chats_text[x]
            main_window.add_widget(ct.get_chatwindow(), row=1, column=2, sticky='news', columnspan=2)
            current_chat_text = ct  # Updates the variable of current text displayed
            current_chat_name = all_chats_button[x].get_button_text()
            # change chat title
            file = open(user_name + "\\connected_users.txt", encoding='utf-8')
            connected_users = file.read() + "#@!#"
            file = open(user_name + "\\last_seen.txt", encoding='utf-8')
            last_seen = file.read()
            file.close()
            t = current_chat_name
            if t + "#@!#" in connected_users:
                t += " (Online)"
                current_chat.change_color(bg="#00b52a", fg="black")
            elif t + " = " in last_seen:
                if "#@!#" in last_seen:
                    last_seen = last_seen.split("#@!#")
                else:
                    last_seen = [last_seen]
                for user in last_seen:
                    if user.startswith(t + " = "):
                        last_seen_with_date_or_without = datetime.now().strftime("%m/%d/%Y, %H:%M")
                        if user.split(" = ")[-1].startswith(last_seen_with_date_or_without[:-5]):
                            seen_time = user.split(" = ")[-1][-5:]
                        else:
                            seen_time = user.split(" = ")[-1]
                        t += "\nLast Seen At " + seen_time
                        break
                current_chat.change_color(bg="#282829", fg="white")
            else:
                current_chat.change_color(bg="#282829", fg="white")
            current_chat.change_text(text=t)
            user_read_msg(user_name, current_chat_name)

        chat = chats_name[i]
        chat_button = Buttonn(chat_buttons.get_chatbuttons(), text=chat, w=36, command=clicked, font="30", bg="#202021",
                              fg="white", h=1)
        if i == new_messages:
            chat_button.change_text(chat + " (%d)" % amount)
            chat_button.new_messages()
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
    except ConnectionRefusedError as err:
        logging.warning(str(err) + " (create_socket)")
        try:
            s.close()
        except Exception as err:
            logging.warning(str(err) + " (create_socket, error while closing the socket)")
        print("Error: Couldn't Connect To Server.\nClosing Program.")
        exit()
    logging.info("Connected to server.")
    return s


def assemble_protocol_and_send(cmd=None, number_of_fields=None, fields=None, data_of_fields=None,
                               file_data=b'', mode='', s=None):
    """
    assembles a message according to the protocol and sends it
    :param cmd: the command the server will handel
    :param number_of_fields: the number of data fields
    :param fields: the name of each field
    :param data_of_fields: the data of each field
    :param file_data: the data of the file if there is
    :param mode: '' or 'upload_file'
    :param s: special socket of the regular socket
    :type cmd: str
    :type number_of_fields: int / str (numbers)
    :type fields: list (of strs)
    :type data_of_fields: list (of strs)
    :type file_data: bytes
    :type mode: str
    :type s: socket.socket
    """
    global user_name, my_socket
    if s is None:
        s = my_socket
    data = cmd + "#@?#" + str(number_of_fields) + "#@?#"
    for field in fields:
        data += field + "#@?#"
    for f_data in data_of_fields:
        data += f_data + "#@?#"
    data = data[:-4]
    data_to_send = ""
    for char in data:
        data_to_send += str(ord(char)) + ","
    try:
        len_and_username = str(len(data_to_send)).ljust(16) + user_name.rjust(16, '#')
        while len(len_and_username) > 0:
            d = s.send(len_and_username.encode())
            len_and_username = len_and_username[d:]
        while len(data_to_send) > 0:
            d = s.send(data_to_send.encode())
            data_to_send = data_to_send[d:]
        if mode == "upload_file":
            while len(file_data) > 0:
                d = s.send(file_data)
                file_data = file_data[d:]
    except Exception as err:
        logging.warning(str(err) + " (assemble_protocol_and_send)")
        try:
            s.close()
        except Exception as err:
            logging.warning(str(err) + " (assemble_protocol_and_send, error while closing the socket)")
        finally:
            print("Error: Lost Connection To Server.\nClosing Program.")
            exit()


def receive_and_disassemble_protocol():
    """
    receives a message according to the protocol and disassembles it
    :return: the fields and the data of fields from the msg
    """
    global my_socket
    data = ""
    left_to_receive = R_SIZE
    try:
        while left_to_receive > 0:
            r = my_socket.recv(left_to_receive).decode()
            data += r
            left_to_receive = R_SIZE - len(data)
            if r == '':
                try:  # try to close the socket
                    my_socket.close()
                except Exception as err:
                    logging.warning(str(err) + " (receive_and_disassemble_protocol, error while closing the socket)")
                    print("Error: Lost Connection To Server.\nClosing Program.")
                    exit()
    except Exception as err:
        logging.warning(str(err) + " (receive_and_disassemble_protocol)")
        print("Error: Lost Connection To Server.\nClosing Program.")
        exit()
    user_name = ""
    left_to_receive = R_SIZE
    try:
        while left_to_receive > 0:
            r = my_socket.recv(left_to_receive).decode()
            user_name += r
            left_to_receive = R_SIZE - len(user_name)
            if r == '':
                try:  # try to close the socket
                    my_socket.close()
                except Exception as err:
                    logging.warning(str(err) + " (receive_and_disassemble_protocol, error while closing the socket)")
                    print("Error: Lost Connection To Server.\nClosing Program.")
                    exit()
    except Exception as err:
        logging.warning(str(err) + " (receive_and_disassemble_protocol)")
        print("Error: Lost Connection To Server.\nClosing Program.")
        exit()
    while '#' in user_name:
        i = user_name.index('#')
        user_name = user_name[:i] + user_name[i + 1:]
    data_len = ""
    for char in data:
        if char.isnumeric():
            data_len += char
    data_len = int(data_len)
    left_to_receive = data_len
    data = ""
    try:
        while left_to_receive > 0:
            r = my_socket.recv(left_to_receive).decode()
            data += r
            left_to_receive = data_len - len(data)
            if r == '':
                try:  # try to close the socket
                    my_socket.close()
                except Exception as err:
                    logging.warning(str(err) + " (receive_and_disassemble_protocol, error while closing the socket)")
                    print("Error: Lost Connection To Server.\nClosing Program.")
                    exit()
    except Exception as err:
        logging.warning(str(err) + " (receive_and_disassemble_protocol)")
        print("Error: Lost Connection To Server.\nClosing Program.")
        exit()
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


def log_in(username='', password=''):
    """
    asks for username and password, send to server, returns server answer
    :param username: in case the user just signed up he can choose to log in automatically, so we need a parameter
    :param password: same as username
    :type username: str
    :type password: str
    :return: True/False, the username that the user typed, a msg that says if login is successful or not
    """
    if username == '' and password == '':
        username = input("Enter Your User Name:         -->  ")
        username_flag = True
        while username_flag:
            while len(username) > 16:
                print("User Name Max Characters Is 16.")
                username = input("Enter Your User Name:         -->  ")
            while len(username) == 0:
                print("Please Enter Something")
                username = input("Enter Your User Name:         -->  ")
            for i in range(0, len(username)):
                char = username[i]
                if char not in USERNAME_ALLOWED_CHARS:
                    print("You entered a char that is not allowed, allowed chars: '%s'" % USERNAME_ALLOWED_CHARS)
                    username = input("Enter Your User Name:         -->  ")
                    break
                else:
                    if i == len(username) - 1:
                        username_flag = False
        password = input("Enter Your Password:          -->  ")
        password_flag = True
        while password_flag:
            if len(password) == 0:
                print("Please Enter Something")
                password = input("Enter Your Password:          -->  ")
            for i in range(0, len(password)):
                char = password[i]
                if char not in USERNAME_ALLOWED_CHARS:
                    print("You entered a char that is not allowed, allowed chars: '%s'" % USERNAME_ALLOWED_CHARS)
                    password = input("Enter Your Password:          -->  ")
                    break
                else:
                    if i == len(password) - 1:
                        password_flag = False
    assemble_protocol_and_send(cmd="login", number_of_fields=2, fields=["user_name", "password"],
                               data_of_fields=[username, password])
    fields, data_of_fields = receive_and_disassemble_protocol()
    if data_of_fields[0] == 'True':
        return True, username, data_of_fields[2]
    else:
        return False, username, data_of_fields[2]


def sign_up():
    """
    asks for username and password, send to server, returns server answer
    :return: True/False, the username that the user typed, a msg that says if signup is successful or not
    """
    user_name = input("Enter Your User Desired Name: -->  ")
    username_flag = True
    while username_flag:
        while len(user_name) > 16:
            print("User Name Max Characters Is 16.")
            user_name = input("Enter Your User Desired Name: -->  ")
        while len(user_name) == 0:
            print("Please Enter Something")
            user_name = input("Enter Your User Desired Name: -->  ")
        for i in range(0, len(user_name)):
            char = user_name[i]
            if char not in USERNAME_ALLOWED_CHARS:
                print("You entered a char that is not allowed, allowed chars: " + USERNAME_ALLOWED_CHARS)
                user_name = input("Enter Your User Desired Name: -->  ")
                break
            else:
                if i == len(user_name) - 1:
                    username_flag = False
    password = input("Enter Your Password:          -->  ")
    password_flag = True
    while password_flag:
        for i in range(0, len(password)):
            char = password[i]
            if char not in USERNAME_ALLOWED_CHARS:
                print("You entered a char that is not allowed, allowed chars: " + USERNAME_ALLOWED_CHARS)
                password = input("Enter Your Password:          -->  ")
                break
            else:
                if i == len(password) - 1:
                    password_flag = False
    assemble_protocol_and_send(cmd="signup", number_of_fields=2, fields=["user_name", "password"],
                               data_of_fields=[user_name, password])
    fields, data_of_fields = receive_and_disassemble_protocol()
    if data_of_fields[0] == 'True':
        return True, user_name, data_of_fields[2], password
    else:
        return False, user_name, data_of_fields[2], password


def sync(sync_socket, first_time="False"):
    """
    syncs all files of user with the server
    :param sync_socket: the socket to use for the synchronization
    :param first_time: if it's the first sync then 'True' else 'False'
    :type sync_socket: socket.socket
    :type first_time: str ('True' or 'False')
    :return: True if there is new data else False
    """
    global current_chat_name, user_name
    first_time = str(first_time)
    assemble_protocol_and_send(cmd="sync", number_of_fields=2, fields=["user_name", "first_time"],
                               data_of_fields=[user_name, first_time], s=sync_socket)
    data = ""
    left_to_receive = R_SIZE
    try:
        while left_to_receive > 0:  # receive number of files
            r = sync_socket.recv(left_to_receive).decode()
            data += r
            left_to_receive = R_SIZE - len(data)
            if r == '':
                try:  # try to close the socket
                    sync_socket.close()
                except Exception as err:
                    logging.warning(str(err) + " (sync, error while closing the socket)")
                    print("Error: Lost Connection To Server.\nClosing Program.")
                    exit()
    except Exception as err:
        logging.warning(str(err) + " (sync)")
        print("Error: Connection To Server.\nClosing Program.")
        exit()
    number_of_chats = ""
    for char in data:  # convert data to a number (for example '2               ' to 2)
        if char.isnumeric():
            number_of_chats += char
    number_of_chats = int(number_of_chats)
    chats_name_and_len = []
    chats_data = []
    try:
        while number_of_chats > 0:  # receive each files name and len
            left_to_receive = 40
            chat = ""
            data_len = ""
            while left_to_receive > 0:  # receive file name
                r = sync_socket.recv(left_to_receive).decode()
                chat += r
                left_to_receive = 40 - len(chat)
                if r == '':
                    try:  # try to close the socket
                        sync_socket.close()
                    except Exception as err:
                        logging.warning(str(err) + " (sync, error while closing the socket)")
                        print("Error: Lost Connection To Server.\nClosing Program.")
                        exit()
            left_to_receive = R_SIZE
            while left_to_receive > 0:  # receive file len
                r = sync_socket.recv(left_to_receive).decode()
                data_len += r
                left_to_receive = R_SIZE - len(data_len)
                if r == '':
                    try:  # try to close the socket
                        sync_socket.close()
                    except Exception as err:
                        logging.warning(str(err) + " (sync, error while closing the socket)")
                        print("Error: Lost Connection To Server.\nClosing Program.")
                        exit()
            while chat[-1] == ' ':
                chat = chat[:-1]
            while data_len[-1] == ' ':
                data_len = data_len[:-1]
            chats_name_and_len.append((chat, data_len))
            number_of_chats -= 1
    except Exception as err:
        logging.warning(str(err) + " (sync)")
        print("Error: Connection To Server.\nClosing Program.")
        exit()
    for chat_name_and_len in chats_name_and_len:  # receive all the files data
        c_name, c_len = chat_name_and_len
        c_data = b''
        left_to_receive = int(c_len)
        try:
            while left_to_receive > 0:  # receive file data
                r = sync_socket.recv(left_to_receive)
                c_data += r
                left_to_receive = int(c_len) - len(c_data)
                if r == b'':
                    try:  # try to close the socket
                        sync_socket.close()
                    except Exception as err:
                        logging.warning(str(err) + " (sync, error while closing the socket)")
                        print("Error: Lost Connection To Server.\nClosing Program.")
                        exit()
        except Exception as err:
            logging.warning(str(err) + " (sync)")
            print("Error: Connection To Server.\nClosing Program.")
            exit()
        chats_data.append(c_data)
    user_read_msg(user_name, current_chat_name)
    if b"No Changes" != chats_data[0]:  # if there are files it will write each file
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
    :param chat_with: the username of the person the msg is for
    :param msg_box: the msg box in the gui
    :type chat_with: str
    :type msg_box: tkinter.Entry
    """
    global user_name
    if " (Online)" in chat_with:  # remove the online status if there is
        chat_with = chat_with[:-9]
    if "\nLast Seen At " in chat_with:  # remove the last seen data if there is
        chat_with = chat_with.split("\n")[0]
    if chat_with != "Home":  # send button only works in a chat
        msg = msg_box.get()
        # check that all the chars are allowed
        i = 0
        while i < len(msg):
            if msg[i] not in ALLOWED:
                msg = msg[:i] + msg[i + 1:]
                i -= 1
            i += 1
        # if the msg contains spam spaces it will remove them
        # it also prevents from sending just spaces because at the end the msg will
        # be '' there is an if statement after the prevents blank messages from being sent
        while msg.endswith(' '):
            msg = msg[:-1]
        while msg.startswith(' '):
            msg = msg[1:]
        # if you send this '*\n*' in your msg it will go a row down
        # this prevents this '*\n*' from being at the start/end of the msg,
        # and it prevents this '*\n*' from being more than twice in a row
        if r"*\n*" in msg:
            msg = msg.split(r"*\n*")
            i = 0
            while i < len(msg) - 1:
                if msg[i] == "" and msg[i + 1] == "":
                    del msg[i]
                    i -= 1
                i += 1
            if msg[-1] == "":
                del msg[-1]
            if msg[0] == "":
                del msg[0]
            msg = r"*\n*".join(msg)
        # block blank messages
        if "" == msg:
            msg_box.delete(0, END)
        # can't send things that effect the protocol/special msgs (unread messages notification and deleted msgs)
        elif "#@?#" in msg:
            msg_box.delete(0, END)
            msg_box.insert("end", "Error Can't Send This")
        elif "#@?!#" in msg:
            msg_box.delete(0, END)
            msg_box.insert("end", "Error Can't Send This")
        elif "#@!#" in msg:
            msg_box.delete(0, END)
            msg_box.insert("end", "Error Can't Send This")
        elif "#@??##" in msg:
            msg_box.delete(0, END)
            msg_box.insert("end", "Error Can't Send This")
        elif "#@?!?##*" in msg:
            msg_box.delete(0, END)
            msg_box.insert("end", "Error Can't Send This")
        elif "#@##@!?#Don'tDisplay" in msg:
            msg_box.delete(0, END)
            msg_box.insert("end", "Error Can't Send This")
        elif "#@##@!?#This Message Was Deleted." in msg:
            msg_box.delete(0, END)
            msg_box.insert("end", "Error Can't Send This")
        else:  # if the msg doesn't contain anything that is not allowed it will be sent
            msg_box.delete(0, END)
            user_read_msg(user_name, current_chat_name)
            assemble_protocol_and_send(cmd="send_msg", number_of_fields=3, fields=["user_name", "chat_with", "msg"],
                                       data_of_fields=[user_name, chat_with, msg])
            fields, data_of_fields = receive_and_disassemble_protocol()
            while fields[0] == "ok" and data_of_fields[0] == "False":
                assemble_protocol_and_send(cmd="send_msg", number_of_fields=3, fields=["user_name", "chat_with", "msg"],
                                           data_of_fields=[user_name, chat_with, msg])
                fields, data_of_fields = receive_and_disassemble_protocol()


def user_read_msg(user_name, other_username):
    """
    updates the server that the user read a message
    :param user_name: the username of this user
    :param other_username: the username of the user that sent the message
    :type user_name: str
    :type other_username: str
    """
    assemble_protocol_and_send(cmd="read", number_of_fields=2, fields=["user_name", "other_username"],
                               data_of_fields=[user_name, other_username])


def sync_():
    """ a function that calls the sync function non-stop"""
    global chat_data, user_name
    sync_socket = create_socket()
    try:
        sync(sync_socket, first_time="True")
        update_gui()
        while True:
            new_data = sync(sync_socket)
            if new_data:
                update_gui()
            time.sleep(0.2)
    except Exception as err:
        logging.warning(str(err) + " (sync_)")
    finally:
        try:
            sync_socket.close()
        except Exception as err:
            logging.warning(str(err) + " (sync_, error while closing the socket)")


def upload_file__(other_username, filename="", root=None, event=None):
    """
    a function that creates a thread to upload a file
    in order to run it in the background so the gui won't get stuck
    :param other_username: the username of the user that the file is sent to
    :param filename: the path to the file
    :param event: because this function is called from a button press it can send this func an event
    :param root: if this func is called to send a voice recording it will close the options window
                 of the voice recording
    :type other_username: str
    :type filename: str
    :type root: tkinter.Tk
    """
    upload_thread = Thread(target=upload_file, args=(other_username, filename,), daemon=True)
    upload_thread.start()
    if root is not None:
        root.destroy()


def upload_file(other_username, filename=""):
    """
    a function to upload a file
    :param other_username: the username of the user that the file is sent to
    :param filename: the path to the file
    :type other_username: str
    :type filename: str
    """
    global user_name
    if " (Online)" in other_username:
        other_username = other_username[:-9]
    if "\nLast Seen At " in other_username:  # remove the last seen data if there is
        other_username = other_username.split("\n")[0]
    if other_username != "Home":
        if filename == "":
            filename = filedialog.askopenfilename()
        if filename != "":
            upload_socket = create_socket()
            try:
                file = open(filename, 'rb')
                file_data = file.read()
                file.close()
                file_size = str(len(file_data))
                file_ends_with = '.' + filename.split('.')[-1]
                assemble_protocol_and_send(cmd="upload_file", number_of_fields=4,
                                           fields=["user_name", "other_username", "file_size", "filename.?"],
                                           data_of_fields=[user_name, other_username, file_size, file_ends_with],
                                           s=upload_socket, mode="upload_file",
                                           file_data=file_data)
                if filename == r"%s\temp.wav" % user_name:
                    os.remove(r"%s\temp.wav" % user_name)
            except Exception as err:
                logging.warning(str(err) + " (upload_file)")
            finally:
                try:
                    upload_socket.close()
                except Exception as err:
                    logging.warning(str(err) + " (upload_file, error while closing the socket)")


def new_chat(entry_box, my_username):
    """
    if the username that the user want to text with exists it will open a new chat with him and display it
    if the user already has a chat with that user it will display it
    :param entry_box: the entry box of the user search
    :param my_username: the username of this user
    :type entry_box: EntryBox
    :type my_username: str
    """
    global current_chat_text, current_chat, current_chat_name
    other_username = entry_box.get_text()
    if other_username == "Home":
        current_chat_name = "Home"
        entry_box.clear()
        entry_box.insert("Start a new chat")
        update_gui()
        return
    if any(char not in USERNAME_ALLOWED_CHARS for char in other_username):
        entry_box.clear()
        entry_box.insert("Invalid User Name")
    elif other_username == "" or other_username == "Start a new chat" or other_username == "Error" or \
            other_username == "Please Type A User Name" or other_username == "You Can't Start A Chat With Yourself" or \
            other_username == "Username Doesn't Exists" or other_username == "Chat Already Exists" or \
            other_username == "Invalid User Name":
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
        assemble_protocol_and_send(cmd="chat_with", number_of_fields=2, fields=["user_name", "chat_with"],
                                   data_of_fields=[my_username, other_username])
        fields, data_of_fields = receive_and_disassemble_protocol()
        if data_of_fields[0] == "False":
            entry_box.clear()
            entry_box.insert(data_of_fields[1])
            if data_of_fields[1] == "Chat Already Exists" and current_chat_name != other_username:
                current_chat_name = other_username
                update_gui()
        else:
            current_chat_name = other_username


def gui():
    """ Initializes The GUI """
    global user_name, msg_box, main_window, chat_buttons, current_chat, home_chat, \
        search_username, current_chat_text, current_chat_name, record_button
    # Create the gui window
    main_window = MainWindow(window_name=user_name)
    root = main_window.get_root()
    # Create a text box that will contain chats buttons
    chat_buttons = ChatButtons()
    main_window.add_widget(chat_buttons.get_chatbuttons(), row=1, column=0, columnspan=2, rowspan=2, sticky='news')
    # Create chat title (name of other username and stats)
    current_chat = Labell(root, text="Home", h=2, font="bold", bg="#282829", fg="white", justify="center")
    main_window.add_widget(current_chat.get_label(), row=0, column=2, sticky='news', columnspan=2)
    # Create an entry box for text
    msg_box = EntryBox(root, w=121, borderwidth=3, bg="#202021", fg="white", font=("helvetica", 16))
    msg_box.bind('<KeyPress>', enter_key)
    main_window.add_widget(msg_box.get_entry(), row=19, column=2, sticky='news')
    # Create a button to record audio
    photo = PhotoImage(file=resource_path("microphone.png"))
    record_button = Buttonn(root, image=photo, command=record_, bg="#202021", h=68, w=140, fg="#63C8D8")
    record_button.change_text("Record")
    main_window.add_widget(record_button.get_button(), row=19, column=3, sticky='news')
    # Create a button to submit the input from the input box
    photo2 = PhotoImage(file=resource_path("send.png"))
    send_msg = Buttonn(root, image=photo2, w=40, h=3, borderwidth=3, bg="#202021", fg="white", font=None,
                       command=lambda: send_message(current_chat.get_label_text(), msg_box.get_entry()))
    main_window.add_widget(send_msg.get_button(), row=19, column=0, sticky='news')
    # Create a button to upload files
    photo3 = PhotoImage(file=resource_path("doc.png"))
    file_upload = Buttonn(root, image=photo3, bg="#202021",
                          command=lambda: upload_file__(current_chat.get_label_text()), h=1, w=1)
    main_window.add_widget(file_upload.get_button(), row=19, column=1, sticky='news')
    # Home window
    home_chat = ChatWindow(root)
    home_chat.home_chat()
    main_window.add_widget(home_chat.get_chatwindow(), row=1, column=2, sticky='news', columnspan=2)
    current_chat_text = home_chat
    current_chat_name = "Home"
    # Create an input box to search a username and start chat with him
    search_username = EntryBox(root, w=40, font=None)
    search_username.bind('<Button-1>', search_delete_on_click)
    search_username.bind('<KeyPress>', enter_key_search_user)
    search_username.insert("Start a new chat")
    main_window.add_widget(search_username.get_entry(), row=0, column=0, sticky='news')
    # Create a button to submit the input from the input box
    search_chat = Buttonn(root, text="Search", w=8, h=1, borderwidth=3, bg="#202021", fg="white",
                          command=lambda: new_chat(search_username, user_name), font=None)
    main_window.add_widget(search_chat.get_button(), row=0, column=1, sticky='news')
    sync_thread = Thread(target=sync_, daemon=True)
    sync_thread.start()
    root.mainloop()


def main():
    # Logging dir and configuration
    if not os.path.isdir(LOG_DIR):
        os.makedirs(LOG_DIR)
    logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)
    global my_socket, user_name
    user_name = ""
    user_password = ""
    my_socket = create_socket()
    login_or_signup = input("Login Or Signup? [L/S]        -->  ")
    while login_or_signup != 'L' and login_or_signup != 'S':
        login_or_signup = input("Enter A Valid Answer [L/S]    -->  ")
    if login_or_signup == 'L':
        login_status = False
        status_data = ""
        while not login_status and status_data != "User Already Connected":
            login_status, user_name, status_data = log_in()
            print("------------------------------------------")
            print(status_data)
            print("------------------------------------------")
    else:
        signup_status = False
        while not signup_status:
            signup_status, user_name, status_data, user_password = sign_up()
            print("------------------------------------------")
            print(status_data)
            print("------------------------------------------")
        auto_login = input("Do You Want To Login As '%s'? [Y/]  -->  " % user_name)
        if auto_login == "Y":
            login_status, user_name, status_data = log_in(username=user_name, password=user_password)
            print("------------------------------------------")
            print(status_data)
            print("------------------------------------------")
        else:
            login_status = False
            status_data = ""
            while not login_status and status_data != "User Already Connected":
                login_status, user_name, status_data = log_in()
                print("------------------------------------------")
                print(status_data)
                print("------------------------------------------")
    if login_status:
        logging.info(user_name + " Logged In Successfully")
        try:
            # Remove the user folder if it exists for some reason
            # If the folder exists it means that last time the program didn't close as it should
            if os.path.isdir(user_name):
                shutil.rmtree(user_name)
            gui()
        except Exception as err:
            logging.warning(str(err))
            print("Connection To Server Error, Please Restart The Program")
        finally:
            try:
                my_socket.close()
            except Exception as err:
                logging.warning(str(err) + " (main, error while closing the socket)")
            # Delete the data of the user
            if os.path.isdir(user_name):
                shutil.rmtree(user_name)
    else:
        logging.debug(user_name + " Logging Failed")
        try:
            my_socket.close()
        except Exception as err:
            logging.warning(str(err) + " (main, error while closing the socket)")


if __name__ == '__main__':
    main()
