"""
Author: Omer Dagry
Program name: The big rebellion
Description: Encrypts and decrypts data (encrypted data saved to file, to choose encryption/decryption pass one of the
             following parameters through sys.argv - encrypt/decrypt)
Date: 14.9.2021
"""
import sys


def start():
    """
    This func checks if the user wants to encrypt/decrypt
    :return: nothing
    """
    if sys.argv[1] == "encrypt":  # checks if the user wants to encrypt, if so call the func encrypt
        encrypt()
    elif sys.argv[1] == "decrypt":  # checks if the user wants to decrypt, if so call the func decrypt
        decryption()


def encrypt():
    """
    This func encrypts the data that the user will type, and saves it to a file
    :param ENCRYPTION_VALUES: dict to convert letters and signs to numbers
    :param DATA: the data that the user wants to encrypt
    :param file: file to write the encrypted data
    :type ENCRYPTION_VALUES: dict
    :type DATA: str
    :type file: '_io.TextIOWrapper'
    :return: nothing
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
    DATA = input("Please enter the message you'd like to encrypt: ")  # get the data to encrypt
    # if the data is nothing it create an empty file
    if DATA == "":
        file = open("encrypted_msg.txt", 'w')  # open file
        file.write("")
        file.close()
    # else it encrypts the data and writes the encrypted data to the file
    file = open("encrypted_msg.txt", 'w')  # open file
    for char in DATA:
        file.write(ENCRYPTION_VALUES[char])  # write to file
    file.close()
    print("Data was encrypted successfully!")


def decryption():
    """
    This func decrypts the data in the file and prints it
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
    :return: nothing
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
        file = open("encrypted_msg.txt", 'r')  # open file
    except FileNotFoundError:
        # if the file doesn't exist print a message and will exit the program
        print("There was no data to decrypt, file does not exist.\nClosing the program...")
        exit()
    ENCRYPTED_DATA = file.read()  # read data from "file"
    # check if there is no data in file
    if ENCRYPTED_DATA == "":
        print()
        exit() # exits program if there is no data to decrypt
    encrypted_data_list = ENCRYPTED_DATA.split(",")  # split the data by commas
    # deletes the last item on list because it is empty(because in the encryption side for each letter that i converted
    # to a number i added a comma after so i'll be able to separate in the decryption so the last char in the file
    # is "," and then i get an empty item that i need to delete
    del encrypted_data_list[-1]
    decrypted_data = ""
    # for loop to get all the items in encrypted_data_list to convert them
    for item in encrypted_data_list:
        decrypted_data += DECRYPTION_VALUES[item]
    print(decrypted_data)


def main():
    start()


if __name__ == '__main__':
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
