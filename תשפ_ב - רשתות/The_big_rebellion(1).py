"""
Author: Omer Dagry
Program name: The big rebellion
Description: Encrypts and decrypts data (encrypted data saved to file, to choose encryption/decryption pass one of the
             following parameters through sys.argv - encrypt/decrypt)
Date: 14.9.2021
"""
import sys


class EncryptionCharError(Exception):
    """Raise when there is a char that can't be encrypted"""


class DecryptionValueError(Exception):
    """Raise when there is a value that can't be decrypted"""


def check_process():
    """
    This func checks the encryption and decryption process
    :param conformation: the msg that the encryption returned
    :param why: AssertionError msg
    :param data: the data from the file (that has the encryption results)
    :param ENCRYPTION_CHECK: the data that suppose to be in the file (in order to check if it is equal)
    :type conformation: str
    :type why: str
    :type data: str
    :type ENCRYPTION_CHECK: str
    :return: if something went wrong tuple(false, msg that says what failed)
             if everything went well tuple(true, msg)
    :rtype: tuple
    """
    # tries to call encrypt with all the chars that it is suppose to be able to encrypt
    try:
        conformation = encryption("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz ,.'!-", "check_process.txt")
    # if AssertionError occurred it returns a tuple(false, why it failed)
    except EncryptionCharError as why:
        return tuple([False, "Encryption process failed, " + str(why)])
    # checks if the encrypt process ended successfully
    if conformation == "Data was encrypted successfully!":
        file = open("check_process.txt", 'r')  # open file to check output
        data = file.read()
        file.close()
        ENCRYPTION_CHECK = "56,57,58,59,40,41,42,43,44,45,46,47,48,49,60,61,62,63,64,65,66,67,68,69,10,11,12,13,14,15,"\
                           "16,17,18,19,30,31,32,33,34,35,36,37,38,39,90,91,92,93,94,95,96,97,98,99,100,101,102,103,"
        # checks if the encrypted data is correct
        # if not returns tuple(false, msg)
        if data != ENCRYPTION_CHECK:
            return tuple([False, "Encryption failed (incorrect values)"])
    # tries to call decryption with all the values that it is suppose to be able to decrypt
    try:
        data = decryption("check_process.txt")
    # if AssertionError occurred it returns a tuple(false, why it failed)
    except DecryptionValueError as why:
        return tuple([False, "Decryption process failed, " + str(why)])
    # checks if decrypted data is correct
    # if not returns tuple(false, msg)
    if data != "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz ,.'!-":
        return tuple([False, "Decryption check failed (incorrect values)"])
    # if everything went well returns tuple(true, msg)
    return tuple([True, "OK"])


def start():
    """
    This func checks if the user wants to encrypt/decrypt
    :return: nothing
    """
    if sys.argv[1] == "encrypt":  # checks if the user wants to encrypt, if so call the func encrypt
        conformation = encryption(input("Please enter the message you'd like to encrypt: "))
        print(conformation)  # get the data to encrypt
    elif sys.argv[1] == "decrypt":  # checks if the user wants to decrypt, if so call the func decrypt
        data = decryption()
        print(data)


def encryption(data, file_path="encrypted_msg.txt"):
    """
    This func encrypts the data that the user will type, and saves it to a file
    :param data: the data that the user wants to encrypt
    :param file_path: the path of the file you want to write the results to
    :param ENCRYPTION_VALUES: dict to convert letters and signs to numbers
    :param file: file to write the encrypted data
    :type data: str
    :type file_path: str
    :type ENCRYPTION_VALUES: dict
    :type file: '_io.TextIOWrapper'
    :return: "Data was encrypted successfully!" if no error occurred
    """
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
    # if the data is nothing it create an empty file
    if data == "":
        file = open(file_path, 'w')  # open file
        file.write("")
        file.close()
    # else it encrypts the data and writes the encrypted data to the file
    file = open(file_path, 'w')  # open file
    for char in data:
        if char not in ENCRYPTION_VALUES:
            raise EncryptionCharError("The char '%s' can't be encrypted" % char)
        file.write(ENCRYPTION_VALUES[char])  # write to file
    file.close()
    return "Data was encrypted successfully!"


def decryption(file_path="encrypted_msg.txt"):
    """
    This func decrypts the data in the file and prints it
    :param file_path: the path of the file from which you want to read the encrypted data
    :param DECRYPTION_VALUES: dict to convert numbers to letters and signs
    :param file: file to read the encrypted data
    :param ENCRYPTED_DATA: the encrypted data from the file
    :param encrypted_data_list: a list of all the numbers in the file
    :param decrypted_data: the decrypted data
    :type DECRYPTION_VALUES: dict
    :type file: '_io.TextIOWrapper'
    :type ENCRYPTED_DATA: str
    :type encrypted_data_list: list
    :type decrypted_data: str
    :return: decrypted data
    """
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
    try:
        file = open(file_path, 'r')  # open file
    except FileNotFoundError:
        # if the file doesn't exist print a message and will exit the program
        print("There was no data to decrypt, file does not exist.\nClosing the program...")
        exit()
    ENCRYPTED_DATA = file.read()  # read data from "file"
    # check if there is no data in file
    if ENCRYPTED_DATA == "":
        print()
        exit()  # exits program if there is no data to decrypt
    encrypted_data_list = ENCRYPTED_DATA.split(",")  # split the data by commas
    # deletes the last item on list because it is empty(because in the encryption side for each letter that i converted
    # to a number i added a comma after so i'll be able to separate in the decryption so the last char in the file
    # is "," and then i get an empty item that i need to delete
    del encrypted_data_list[-1]
    decrypted_data = ""
    # for loop to get all the items in encrypted_data_list to convert them
    for item in encrypted_data_list:
        if item not in DECRYPTION_VALUES:
            raise DecryptionValueError("The number '%s' can't be converted to anything" % item)
        decrypted_data += DECRYPTION_VALUES[item]
    return decrypted_data


def main():
    start()


if __name__ == '__main__':
    assert check_process()[0], check_process()[1]
    while True:
        try:
            assert len(sys.argv) >= 2
            break
        except AssertionError:
            what_to_do = input("Please enter one of these options (encrypt/decrypt): ")
            if what_to_do == "encrypt" or what_to_do == "decrypt":
                sys.argv.append(what_to_do)
                break
    while True:
        try:
            assert sys.argv[1] == "encrypt" or sys.argv[1] == "decrypt"
            break
        except AssertionError:
            what_to_do = input("Please enter a valid option (encrypt/decrypt): ")
            if what_to_do == "encrypt" or what_to_do == "decrypt":
                sys.argv[1] = what_to_do
                break
    main()
