import sys
from math import ceil


def encrypt(data, key):
    key = int(key)
    list_data = []
    while len(data) % key != 0:
        data += " "
    for i in range(0, len(data) // key):
        list_data.append("")
    for i in range(0, len(data)):
        list_data[i//key] += data[i]
    encrypted_data = ""
    for i in range(0, key):
        for item in list_data:
            encrypted_data += item[i]
    return encrypted_data


def decrypt(encrypted_data, key):
    key = ceil(len(encrypted_data) / int(key))
    list_data = []
    while len(encrypted_data) % key != 0:
        encrypted_data += " "
    for i in range(0, len(encrypted_data) // key):
        list_data.append("")
    for i in range(0, len(encrypted_data)):
        list_data[i // key] += encrypted_data[i]
    encrypted_data = ""
    for i in range(0, key):
        for item in list_data:
            encrypted_data += item[i]
    return encrypted_data


def main():
    if sys.argv[1] == "1":
        data = input("please enter message")
        key = input("please enter key (needs to be less or equal to half len data): ")
        while not len(data) // 2 >= len(key):
            key = input("please enter key (needs to be less or equal to half len data): ")
        print(encrypt(data, key))
    if sys.argv[1] == "2":
        encrypted_data = input("please enter encrypted data: ")
        key = input("please enter key: ")
        print(decrypt(encrypted_data, key))


if __name__ == '__main__':
    if not len(sys.argv) > 1:
        sys.argv.append(input("enter mode 1 for encrypt 2 for decrypt: "))
    while sys.argv[1] != "1" and sys.argv[1] != "2":
        sys.argv[1] = input("please enter 1 or 2: ")
    main()
