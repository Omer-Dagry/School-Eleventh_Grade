import sys


def encrypt(data, key):
    encrypted_data = ""
    for char in data:
        encrypted_data += chr((ord(char) - 97 + int(key)) % 26 + 97)
    return encrypted_data


def decrypt(encrypted_data):
    for key in range(0, 27):
        data = ""
        for char in encrypted_data:
            if char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
                data += chr(ord(char) - key)
            else:
                data += char
        print(data)


def main():
    if sys.argv[1] == "1":
        key = input("please enter key(0 -26): ")
        data = input("please enter message")
        print(encrypt(key, data))
    if sys.argv[1] == "2":
        encrypted_data = input("please enter encrypted data: ")
        decrypt(encrypted_data)


if __name__ == '__main__':
    if not len(sys.argv) > 1:
        sys.argv.append(input("1 = Encrypt.\n"
                              "2 = Brute Force Decryption.\n"
                              "To Decrypt enter '1' and the key will be the negative form of the encryption key in.\n"))
    while sys.argv[1] != "1" and sys.argv[1] != "2":
        sys.argv[1] = input("please enter 1 or 2: ")
    main()
