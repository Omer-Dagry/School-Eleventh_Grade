from math import ceil
from english_dictionary_dict import english_dictionary_dict

dup1 = []  # global list


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


def extract_spaces(encrypted_data_input):
    encrypted_data = ""
    special_chars = ""
    special_chars_as_spaces = ""
    for char in encrypted_data_input:
        if char in "abcdefghijklmnopqrstuvwxyz":
            encrypted_data += char
            special_chars += "A"
            special_chars_as_spaces += "A"
        else:
            special_chars += char
            special_chars_as_spaces += " "
    i = 0
    while i < len(special_chars_as_spaces) - 1:
        if special_chars_as_spaces[i] == ' ' and special_chars_as_spaces[i+1] == ' ':
            special_chars_as_spaces = special_chars_as_spaces[:i] + special_chars_as_spaces[i+1:]
            i -= 1
        i += 1
    if special_chars_as_spaces[-1] == ' ':
        special_chars_as_spaces = special_chars_as_spaces[:-1]
    # special_chars_as_spaces_list = special_chars_as_spaces.split(' ')
    # for i in range(0, len(special_chars_as_spaces_list)):
    #     if special_chars_as_spaces_list[i] == '':
    #         del special_chars_as_spaces_list[i]
    return encrypted_data, special_chars, special_chars_as_spaces


def get_key_lengths(encrypted_data):
    global dup1
    flag = False
    encrypted_data += "|"
    duplicates = []
    part_repeated = 0
    for i in range(0, len(encrypted_data)):
        if part_repeated == 0:
            if encrypted_data.count(encrypted_data[i:i + 3]) > 1:
                for j in range(0, len(encrypted_data)):
                    if encrypted_data.count(encrypted_data[i:i + 3 + j]) < 2:
                        if not flag:
                            dup1.append(i)
                            dup1.append(j + 2)
                            flag = True
                        part_repeated = len(encrypted_data[i:i + 3 + j]) - 3
                        duplicates.append(encrypted_data[i:i + 3 + j - 1])
                        duplicates.append(i)
                        break
        else:
            part_repeated -= 1
    duplicates_list_organized = []
    for i in range(0, len(duplicates), 2):
        for j in range(i + 2, len(duplicates), 2):
            if duplicates[i] == duplicates[j]:
                duplicates_list_organized.append(duplicates[i])
                duplicates_list_organized.append(duplicates[j + 1] - duplicates[i + 1])
    key_lengths = []
    for i in range(1, len(duplicates_list_organized), 2):
        for j in range(3, duplicates_list_organized[i] + 1):
            if duplicates_list_organized[i] % j == 0:
                key_lengths.append(j)
    possible_key_lengths = []
    for length in key_lengths:
        if key_lengths.count(length) > 1 and length not in possible_key_lengths:
            possible_key_lengths.append(length)
    if len(possible_key_lengths) > 0:
        possible_key_lengths.sort()
        return possible_key_lengths
    else:
        key_lengths.sort()
        return key_lengths


def same_char_encryption(encrypted_data, length):
    same_char_list = []
    for i in range(0, length):
        same_char_list.append("")
        for j in range(i, len(encrypted_data), length):
            same_char_list[i] += encrypted_data[j]
    return same_char_list


def get_all_options(same_char_list):
    all_options = []
    for data in same_char_list:
        all_options.append([])
        for letter in "abcdefghijklmnopqrstuvwxyz":
            all_options[same_char_list.index(data)].append(decrypt(data, letter))
    return all_options


def brute_force_3(encrypted_data, special_chars_as_spaces, special_chars):
    same_char_list = same_char_encryption(encrypted_data, 3)
    all_options = get_all_options(same_char_list)
    full_option = ""
    count = 0
    flag = False
    count2 = 0
    for option1 in all_options[0]:
        len_option_1 = len(option1)
        for option2 in all_options[1]:
            len_option_2 = len(option2)
            for option3 in all_options[2]:
                for i in range(0, len_option_1):
                    full_option += option1[i]
                    if len_option_2 > i:
                        full_option += option2[i]
                    if len(option3) > i:
                        full_option += option3[i]
                for i in range(0, len(special_chars_as_spaces)):
                    if special_chars_as_spaces[i] == " ":
                        full_option = full_option[:i] + " " + full_option[i:]
                full_option_words_list = full_option.split(' ')
                for word in full_option_words_list:
                    if word in english_dictionary_dict:
                        flag = True
                        count += 1
                if flag:
                    if count / len(full_option_words_list) > 0.5:
                        for i in range(0, len(special_chars)):
                            if special_chars[i] != "A" and special_chars[i] != ' ':
                                full_option = full_option[:i] + special_chars[i] + full_option[i:]
                        print(full_option)
                        continue_y_n = input("Continue? [Y/N]")
                        save_result_y_n = input("Save Result To File? [Y/N]")
                        while True:
                            if save_result_y_n == 'N':
                                break
                            elif save_result_y_n == 'Y':
                                file = open("Vigenere_Brute_Force_Results.txt", 'a')
                                file.write(full_option + "\n")
                                file.close()
                                break
                            else:
                                save_result_y_n = input("Please enter one of these options [Y/N]")
                        while True:
                            if continue_y_n == 'N':
                                print("Decryption Finished.\nClosing Program...")
                                exit()
                            elif continue_y_n == 'Y':
                                break
                            else:
                                continue_y_n = input("Please enter one of these options [Y/N]")
                flag = False
                full_option = ""
                count = 0
                count2 += 1
                print(count2)


def brute_force_4(encrypted_data, special_chars_as_spaces, special_chars):
    same_char_list = same_char_encryption(encrypted_data, 4)
    all_options = get_all_options(same_char_list)
    full_option = ""
    count = 0
    flag = False
    count2 = 0
    for option1 in all_options[0]:
        len_option_1 = len(option1)
        for option2 in all_options[1]:
            len_option_2 = len(option2)
            for option3 in all_options[2]:
                len_option_3 = len(option3)
                for option4 in all_options[3]:
                    for i in range(0, len_option_1):
                        full_option += option1[i]
                        if len_option_2 > i:
                            full_option += option2[i]
                        if len_option_3 > i:
                            full_option += option3[i]
                        if len(option4) > i:
                            full_option += option4[i]
                    for i in range(0, len(special_chars_as_spaces)):
                        if special_chars_as_spaces[i] == " ":
                            full_option = full_option[:i] + " " + full_option[i:]
                    full_option_words_list = full_option.split(' ')
                    for word in full_option_words_list:
                        if word in english_dictionary_dict:
                            flag = True
                            count += 1
                    if flag:
                        if count / len(full_option_words_list) > 0.5:
                            for i in range(0, len(special_chars)):
                                if special_chars[i] != "A" and special_chars[i] != ' ':
                                    full_option = full_option[:i] + special_chars[i] + full_option[i:]
                            print(full_option)
                            continue_y_n = input("Continue? [Y/N]")
                            save_result_y_n = input("Save Result To File? [Y/N]")
                            while True:
                                if save_result_y_n == 'N':
                                    break
                                elif save_result_y_n == 'Y':
                                    file = open("Vigenere_Brute_Force_Results.txt", 'a')
                                    file.write(full_option + "\n")
                                    file.close()
                                    break
                                else:
                                    save_result_y_n = input("Please enter one of these options [Y/N]")
                            while True:
                                if continue_y_n == 'N':
                                    print("Decryption Finished.\nClosing Program...")
                                    exit()
                                elif continue_y_n == 'Y':
                                    break
                                else:
                                    continue_y_n = input("Please enter one of these options [Y/N]")
                    flag = False
                    full_option = ""
                    count = 0
                    count2 += 1
                    print(count2)


def brute_force_5(encrypted_data, special_chars_as_spaces, special_chars):
    same_char_list = same_char_encryption(encrypted_data, 5)
    all_options = get_all_options(same_char_list)
    full_option = ""
    count = 0
    flag = False
    count2 = 0
    for option1 in all_options[0]:
        len_option_1 = len(option1)
        for option2 in all_options[1]:
            len_option_2 = len(option2)
            for option3 in all_options[2]:
                len_option_3 = len(option3)
                for option4 in all_options[3]:
                    len_option_4 = len(option4)
                    for option5 in all_options[4]:
                        for i in range(0, len_option_1):
                            full_option += option1[i]
                            if len_option_2 > i:
                                full_option += option2[i]
                            if len_option_3 > i:
                                full_option += option3[i]
                            if len_option_4 > i:
                                full_option += option4[i]
                            if len(option5) > i:
                                full_option += option5[i]
                        for i in range(0, len(special_chars_as_spaces)):
                            if special_chars_as_spaces[i] == " ":
                                full_option = full_option[:i] + " " + full_option[i:]
                        full_option_words_list = full_option.split(' ')
                        for word in full_option_words_list:
                            if word in english_dictionary_dict:
                                flag = True
                                count += 1
                        if flag:
                            if count / len(full_option_words_list) > 0.5:
                                for i in range(0, len(special_chars)):
                                    if special_chars[i] != "A" and special_chars[i] != ' ':
                                        full_option = full_option[:i] + special_chars[i] + full_option[i:]
                                print(full_option)
                                continue_y_n = input("Continue? [Y/N]")
                                save_result_y_n = input("Save Result To File? [Y/N]")
                                while True:
                                    if save_result_y_n == 'N':
                                        break
                                    elif save_result_y_n == 'Y':
                                        file = open("Vigenere_Brute_Force_Results.txt", 'a')
                                        file.write(full_option + "\n")
                                        file.close()
                                        break
                                    else:
                                        save_result_y_n = input("Please enter one of these options [Y/N]")
                                while True:
                                    if continue_y_n == 'N':
                                        print("Decryption Finished.\nClosing Program...")
                                        exit()
                                    elif continue_y_n == 'Y':
                                        break
                                    else:
                                        continue_y_n = input("Please enter one of these options [Y/N]")
                        flag = False
                        full_option = ""
                        count = 0
                        count2 += 1
                        print(count2)


def main():
    encrypted_data_user = input("Please enter data to decrypt.\n"
                                "This code can only decrypt data that is encrypted with key lengths 3 - 5\n").lower()
    key_length_known = input("Do you know what is the length of the key? [Y/N]: ")
    while True:
        if key_length_known != 'N' and key_length_known != 'Y':
            print("Please enter a valid option [Y/N].")
            key_length_known = input("Do you know what is the length of the key? [Y/N]: ")
        else:
            break
    (encrypted_data, special_chars, special_chars_as_spaces) = extract_spaces(encrypted_data_user)
    if key_length_known == 'N':
        possible_key_lengths = get_key_lengths(encrypted_data)  # get duplicates and their place
        possible_key_lengths_can_decrypt = []
        for length in possible_key_lengths:
            if 0 < length < 6:
                possible_key_lengths_can_decrypt.append(length)
            else:
                break
    else:
        possible_key_lengths_can_decrypt = [int(input("Please enter the key length: "))]
        while True:
            if not 2 < possible_key_lengths_can_decrypt[0] < 6:
                del possible_key_lengths_can_decrypt[0]
                print("This code can only decrypt data that was encrypted with key lengths 3 - 5")
                continue_y_n = input("Enter again? [Y/N]")
                while True:
                    if continue_y_n == 'N':
                        print("Closing Program...")
                        exit()
                    elif continue_y_n == 'Y':
                        possible_key_lengths_can_decrypt = [int(input("Please enter the key length: "))]
                        break
                    else:
                        print("Please enter a valid option [Y/N].")
                        continue_y_n = input("Enter again? [Y/N]")
            else:
                break
    # get the chars that are encrypted with the same char in key
    for length in possible_key_lengths_can_decrypt:
        if length == 3:
            brute_force_3(encrypted_data, special_chars_as_spaces, special_chars)
        if length == 4:
            brute_force_4(encrypted_data, special_chars_as_spaces, special_chars)
        if length == 5:
            brute_force_5(encrypted_data, special_chars_as_spaces, special_chars)


if __name__ == '__main__':
    main()
