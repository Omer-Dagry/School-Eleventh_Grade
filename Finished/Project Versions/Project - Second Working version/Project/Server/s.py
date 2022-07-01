import socket
import os


def log_in():
    user_name = input("Enter Your User Name: ")
    password = input("Enter Your Password: ")
    file = open("users.txt", 'r')
    data = file.read()
    file.close()
    user_password = data.split('\n')
    users = [user_password[i] for i in range(0, len(user_password), 2)]
    passwords = [user_password[i] for i in range(1, len(user_password), 2)]
    if user_name in users:
        count = 3
        while password != passwords[users.index(user_name)] and count != 0:
            print("Wrong Password")
            password = input("Enter Your Password (You Have %d More Tries): " % count)
            count -= 1
        if password == passwords[users.index(user_name)]:
            print("Logged In Successfully")
            return True, user_name
    else:
        print("User Name Doesn't Exists Please Sign Up.")
        return False, 'None'


def sign_up():
    file = open("users.txt", 'r')
    data = file.read()
    file.close()
    user_password = data.split('\n')
    users = [user_password[i] for i in range(0, len(user_password), 2)]
    user_name = input("Enter Your Desired User Name: ")
    while user_name in users or user_name == 'None':
        print("This User Name Is Taken.")
        user_name = input("Enter Your Desired User Name: ")
    password = input("Enter Your Password: ")
    file = open("users.txt", 'w')
    data += user_name + "\n" + password + "\n"
    file.write(data)
    file.close()
    user_char_dir = 'chats\\' + user_name
    os.mkdir(user_char_dir)
    print("Signed Up Successfully")
    return True


def communicate_with(user_name):
    communication_options = os.listdir('chats\\' + user_name)
    i = 0
    while i < len(communication_options):
        if not communication_options[i].endswith(".txt"):
            del communication_options[i]
        else:
            i += 1
    chat_with = input("Please Enter The User Name Of The Person You Want To Chat With: ")
    while chat_with not in os.listdir('chats\\'):
        chat_with = input("This User Name Doesn't Exists Please Enter Another one: ")
    if chat_with + ".txt" not in communication_options:
        file = open('chats\\' + user_name + chat_with + ".txt", 'w')
        file.close()
    return chat_with


def send_message(user_name, chat_with, msg):
    file = open('chats\\' + user_name + chat_with + ".txt", 'r')
    data = file.read()
    file.close()
    file = open('chats\\' + user_name + chat_with + ".txt", 'w')
    data += msg + "\n//**//\n"
    file.write(data)
    file.close()


def main():
    if not os.path.isfile('users.txt'):
        file = open('users.txt', 'w')
        file.close()
    if not os.path.isdir('chats'):
        os.mkdir('chats')
    login_or_signup = input("Do You Have A User? [Y/N] ")
    while login_or_signup != 'Y' and login_or_signup != 'N':
        login_or_signup = input("Please Enter A Valid Answer [Y/N] ")
    if login_or_signup == 'Y':
        login_successfull, user_name = log_in()
    else:
        signup_successfull = False
        while not signup_successfull:
            signup_successfull = sign_up()
        login_successfull, user_name = log_in()
    if login_successfull:
        want_to_chat = True
        while want_to_chat:
            chat_with = communicate_with(user_name)
            print("You Can Now Send Messages to %s, To Stop Enter '!stop!'.")
            msg = input("Message To Send:\n")
            if msg == "!stop!":
                chat_with_someone_else = input("Do You Want To Chat With Someone Else? [Y/N]\n")
                while chat_with_someone_else != 'Y' and chat_with_someone_else != 'N':
                    print("You Entered '%s', That's Not An Option. Please Enter 'Y' Or 'N'." % chat_with_someone_else)
                    chat_with_someone_else = input("Do You Want To Chat With Someone Else? [Y/N]\n")
                if chat_with_someone_else == 'N':
                    want_to_chat = False
            else:
                send_message(user_name, chat_with, msg)


if __name__ == '__main__':
    main()
