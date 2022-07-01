import sys
from math import ceil


def encrypt(data, key):
    key_len_data = ""
    for i in range(0, ceil(len(data) / len(key))):
        key_len_data += key
    for i in range(0, len(data)):
        if data[i] not in "abcdefghijklmnopqrstuvwxyz":
            key_len_data = key_len_data[:i] + " " + key_len_data[i:]
    encrypted_data = ""
    for i in range(0, len(data)):
        if data[i] in "abcdefghijklmnopqrstuvwxyz":
            encrypted_data += chr((ord(data[i]) - 97 + ord(key_len_data[i]) - 97) % 26 + 97)
        else:
            encrypted_data += data[i]
    return encrypted_data


def decrypt(encrypted_data, key):
    key_len_data = ""
    for i in range(0, ceil(len(encrypted_data) / len(key))):
        key_len_data += key
    for i in range(0, len(encrypted_data)):
        if encrypted_data[i] not in "abcdefghijklmnopqrstuvwxyz":
            key_len_data = key_len_data[:i] + " " + key_len_data[i:]
    data = ""
    for i in range(0, len(encrypted_data)):
        if encrypted_data[i] in "abcdefghijklmnopqrstuvwxyz":
            data += chr(abs((ord(encrypted_data[i]) - 97 - (ord(key_len_data[i]) - 97)) % 26 + 97))
        else:
            data += encrypted_data[i]
    return data


def main():
    if sys.argv[1] == "1":
        data = input("please enter message").lower()
        key = input("please enter key: ").lower()
        print(encrypt(data, key))
    if sys.argv[1] == "2":
        encrypted_data = input("please enter encrypted data: ").lower()
        key = input("please enter key: ").lower()
        print(decrypt(encrypted_data, key))


if __name__ == '__main__':
    if not len(sys.argv) > 1:
        sys.argv.append(input("enter mode 1 for encrypt 2 for decrypt: "))
    while sys.argv[1] != "1" and sys.argv[1] != "2":
        sys.argv[1] = input("please enter 1 or 2: ")
    main()
