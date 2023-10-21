"""
Author: Omer Dagry
Program name: The big rebellion
Description: Encrypts and decrypts data (encrypted data saved to file, to choose encryption/decryption pass one of the
             following parameters through sys.argv - encrypt/decrypt)
Date: 17.9.2021
"""
import sys
import logging
import os

# logging
LOG_FORMAT = "%(levelname)s | %(asctime)s | %(processName)s | %(message)s"
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = LOG_DIR + "/The_big_rebellion.log"

# contains the chars that can be encrypted
CAN_ENCRYPT = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz ,.'!-"

# contains the data that can be decrypted
CAN_DECRYPT = [56, 57, 58, 59, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 10, 11,
               12, 13, 14, 15, 16, 17, 18, 19, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 90, 91, 92, 93, 94, 95, 96, 97,
               98, 99, 100, 101, 102, 103]

# contains the encrypted data that suppose to be in the file after the encryption check
VALUES_CHECK = "56,57,58,59,40,41,42,43,44,45,46,47,48,49,60,61,62,63,64,65,66,67,68,69,10,11,12,13,14,15,"\
                           "16,17,18,19,30,31,32,33,34,35,36,37,38,39,90,91,92,93,94,95,96,97,98,99,100,101,102,103"

# dict to encrypt the data
ENCRYPTION_VALUES = {"A": "56,", "B": "57,", "C": "58,", "D": "59,", "E": "40,", "F": "41,", "G": "42,", "H": "43,",
                     "I": "44,", "J": "45,", "K": "46,", "L": "47,", "M": "48,", "N": "49,", "O": "60,", "P": "61,",
                     "Q": "62,", "R": "63,", "S": "64,", "T": "65,", "U": "66,", "V": "67,", "W": "68,", "X": "69,",
                     "Y": "10,", "Z": "11,",
                     "a": "12,", "b": "13,", "c": "14,", "d": "15,", "e": "16,", "f": "17,", "g": "18,", "h": "19,",
                     "i": "30,", "j": "31,", "k": "32,", "l": "33,", "m": "34,", "n": "35,", "o": "36,", "p": "37,",
                     "q": "38,", "r": "39,", "s": "90,", "t": "91,", "u": "92,", "v": "93,", "w": "94,", "x": "95,",
                     "y": "96,", "z": "97,",
                     " ": "98,", ",": "99,", ".": "100,", "'": "101,", "!": "102,", "-": "103,"}

# dict to decrypt the encrypted data
DECRYPTION_VALUES = {"56": "A", "57": "B", "58": "C", "59": "D", "40": "E", "41": "F", "42": "G", "43": "H",
                     "44": "I", "45": "J", "46": "K", "47": "L", "48": "M", "49": "N", "60": "O", "61": "P",
                     "62": "Q", "63": "R", "64": "S", "65": "T", "66": "U", "67": "V", "68": "W", "69": "X",
                     "10": "Y", "11": "Z",
                     "12": "a", "13": "b", "14": "c", "15": "d", "16": "e", "17": "f", "18": "g", "19": "h",
                     "30": "i", "31": "j", "32": "k", "33": "l", "34": "m", "35": "n", "36": "o", "37": "p",
                     "38": "q", "39": "r", "90": "s", "91": "t", "92": "u", "93": "v", "94": "w", "95": "x",
                     "96": "y", "97": "z",
                     "98": " ", "99": ",", "100": ".", "101": "'", "102": "!", "103": "-"}


class EncryptionCharError(Exception):
    """Raise when there is a char that can't be encrypted"""


class DecryptionValueError(Exception):
    """Raise when there is a value that can't be decrypted"""


def check():
    """
    Checks the encryption and decryption process (including validation of data)
    :return: if everything went well - True
             if something failed - False
    :rtype: bool
    """
    global msg
    # validate_data_to_encrypt check
    validate_msg = validate_data_to_encrypt(CAN_ENCRYPT)
    if validate_msg != "OK":
        msg = "validate_data_to_encrypt"
        return False  # fails the assert
    # encryption check
    encrypted_data = encryption(CAN_ENCRYPT)
    # removes the last character because it is an unnecessary comma
    encrypted_data = encrypted_data[:-1]
    if encrypted_data != VALUES_CHECK:
        msg = "encryption"
        return False  # fails the assert
    # write_to_file and read_from_file check
    write_to_file(encrypted_data, "The_big_rebellion_CHECK.txt")
    encrypted_data = read_from_file("The_big_rebellion_CHECK.txt")
    os.remove("The_big_rebellion_CHECK.txt")  # removes the file because it is no longer necessary
    if encrypted_data != VALUES_CHECK:
        msg = "write_to_file or read_from_file"
        return False  # fails the assert
    # validate_data_to_decrypt check
    validate_msg = validate_data_to_decrypt(encrypted_data)
    if validate_msg != "OK":
        msg = "validate_data_to_decrypt"
        return False  # fails the assert
    # decryption check
    decrypted_data = decryption(encrypted_data)
    if decrypted_data != CAN_ENCRYPT:
        msg = "decryption"
        return False  # fails the assert
    # if everything went well
    msg = "OK"
    return True  # assert passes


def user_input(input_msg="Enter input"):
    """
    Asks the user to enter input
    :param input_msg: the message that will be printed when asking the user to enter input
    :return: the input
    :rtype: str
    """
    return input(input_msg)


def read_from_file(file_path="encrypted_msg.txt"):
    """
    Reads data from given file
    :param file_path: the file path you wants to read from
    :return: if file exists - the data in the file
             if file doesn't exists - returns msg
    :rtype: str
    """
    file = open(file_path, 'r')  # open file
    file_data = file.read()  # read data from "file" and returns it
    file.close()
    return file_data


def validate_data_to_encrypt(data):
    """
    Checks if all the chars in 'data' can be encrypted
    :param data: the data we want to check (user input)
    :return: if data can't be encrypted -  "The char '%s' can't be encrypted" % char
             if data can be encrypted - "OK"
    :rtype: str
    """
    for char in data:
        if not (char in CAN_ENCRYPT):
            raise EncryptionCharError("The char '%s' can't be encrypted" % char)
    return "OK"


def validate_data_to_decrypt(data):
    """
    Checks if all the values in 'data' can be decrypted
    :param data: the data we want to check (encrypted data from file)
    :return: if data can't be decrypted - "The value '%s' can't be decrypted" % value
             if data can be decrypted - "OK"
    """
    if data == "":
        return "OK"
    data_list = data.split(',')  # split the data by commas
    for value in data_list:
        if not int(value) in CAN_DECRYPT:
            raise DecryptionValueError("The value '%s' can't be decrypted" % value)
    return "OK"


def encryption(data):
    """
    This func encrypts the user input. call it only after validating user input!!
    :param data: the data we are going to encrypt
    :return: encrypted data
    """
    if data == "":
        return ""
    encrypted_data = ""
    for char in data:
        encrypted_data += ENCRYPTION_VALUES[char]
    return encrypted_data


def decryption(data):
    """
    This func decrypts the encrypted data (from file). call it only after validating the data from the file!!
    :param data: the data we are going to decrypt
    :return: decrypted data
    """
    # check if there is no data in file
    if data == "":
        return ""
    encrypted_data_list = data.split(",")  # split the data by commas
    decrypted_data = ""
    # for loop to get all the items in encrypted_data_list to convert them
    for item in encrypted_data_list:
        decrypted_data += DECRYPTION_VALUES[item]
    return decrypted_data


def write_to_file(data, file_path="encrypted_msg.txt"):
    """
    Writes the given data to a given file (default file - "encrypted_msg.txt")
    :param data: the data to write to the file
    :param file_path: the file path you want to write to (default - "encrypted_msg.txt")
    :return: nothing
    """
    file = open(file_path, 'w')  # open file (creates it if doesn't exists)
    file.write(str(data))  # writes the data to file
    file.close()  # closes the file


def main():
    if not os.path.isdir(LOG_DIR):
        os.makedirs(LOG_DIR)
    logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)
    logging.debug("User passed through sys.argv the word '%s'" % sys.argv[1])
    if sys.argv[1] == "encrypt":
        logging.info("mode = encrypt")
        data = user_input("Please enter data to encrypt:\n")
        logging.debug("user entered: '%s'" % data)
        try:
            validate_msg = validate_data_to_encrypt(data)
        except EncryptionCharError as why:
            logging.warning("User input was identified as invalid, " + str(why))
            print(why)
            exit()
        encrypted_data = encryption(data)
        # removes the last character because it is an unnecessary comma
        encrypted_data = encrypted_data[:-1]
        logging.info("Encrypted data: '%s'" % encrypted_data)
        write_to_file(encrypted_data)
        print("\nData was encrypted successfully and saved to a file\n")
    # I don't need to do another if and check if sys.argv[1] == "decrypt" because before main() i forced the user to
    # enter either "encrypt" or "decrypt", so if sys.argv[1] != "encrypt" it has to be equal to "decrypt"
    else:
        logging.info("mode = decrypt")
        try:
            encrypted_data = read_from_file()
            logging.info("Data to decrypt: '%s'" % encrypted_data)
        except FileNotFoundError:
            print("There was no data to read, file doesn't exist.")
            logging.warning("File doesn't exist")
            exit()
        try:
            validate_msg = validate_data_to_decrypt(encrypted_data)
        except DecryptionValueError as why:
            print(why)
            logging.warning("Encrypted data in file was identifies as invalid, " + str(why))
            exit()
        if validate_msg == "OK":
            decrypted_data = decryption(encrypted_data)
            logging.info("Decrypted data: " + decrypted_data)
            print(decrypted_data)


if __name__ == '__main__':
    msg = ""
    assert check(), msg
    # makes the user enter something to sys.argv[1] if he didn't already
    while True:
        if len(sys.argv) >= 2:
            break
        else:
            what_to_do = input("Please enter one of these options (encrypt/decrypt): ")
            sys.argv.append(what_to_do)
            break
    # makes the user to enter something valid ("encrypt"/"decrypt") to sys.argv[1] if he didn't already
    while True:
        if sys.argv[1] == "encrypt" or sys.argv[1] == "decrypt":
            break
        else:
            what_to_do = input("Please enter a valid option (encrypt/decrypt): ")
            if what_to_do == "encrypt" or what_to_do == "decrypt":
                sys.argv[1] = what_to_do
                break
    main()
