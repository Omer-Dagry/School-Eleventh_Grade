from math import ceil
from collections import Counter
from english_dictionary_tuple import english_dictionary_tuple

COMMON_LETTERS = "etaoin"
LEAST_COMMON_LETTERS = "zjqxkv"
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
    print(duplicates)
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


def main():
    encrypted_data_input = "ooeh uqqq a ukpe ujhrf yds b fhas nltunh gjto wiq zat nrvff ey fxhrzqqe xjr lpqnee cw hft, euu orsu qi amn ey igu gscqdnqwhft, dne vkesg zat prtikqg ujdt tjh wpwod oqw hbxh gjxhn uq whf ekimf. rndg vhf idvf jhr b nltunh hpqg og thd wgovfv, zhjek svkwee jhr tq zemn whbv vhf yrumf qewgu wfcu aoawhjpj emuh; sp uke xcv amydyt edlmgg 'ljvwlf thd-skgioi-kopf.'".lower()  # input("please enter data to decrypt").lower()
    (encrypted_data, special_chars, special_chars_as_spaces) = extract_spaces(encrypted_data_input)
    possible_key_lengths = get_key_lengths(encrypted_data)  # get duplicates and their place
    print(possible_key_lengths)
    # get the chars that are encrypted with the same char in key
    same_char_list = same_char_encryption(encrypted_data, 4)
    print(len(same_char_list), " ", same_char_list)
    all_options = get_all_options(same_char_list)
    print(len(all_options), " ", all_options)
    list_string_1 = all_options[0]
    list_string_2 = all_options[1]
    list_string_3 = all_options[2]
    list_string_4 = all_options[3]
    # list_string_5 = all_options[4]
    full_option = ""
    count = 0
    flag = False
    attempt_number = 0
    ok = "once upon a time there was a dear little girl who was loved by everyone who looked at her but most of all by her grandmother and there was nothing that she would not have given to the child once she gave her a little hood of red velvet which suited her so well that she would never wear anything else so she was always called little red riding hood"
    if "crypto" in english_dictionary_tuple:
        print("ok")
        ok_list = ok.split(' ')
        for word in ok_list:
            if word not in english_dictionary_tuple:
                print(word)
    else:
        print("not ok")
    len_encrypted_data = len(encrypted_data)
    for option1 in list_string_1:
        len_option_1 = len(option1)
        for option2 in list_string_2:
            len_option_2 = len(option2)
            for option3 in list_string_3:
                len_option_3 = len(option3)
                for option4 in list_string_4:
                    for i in range(0, len_option_1):
                        full_option += option1[i]
                        if len_option_2 > i:
                            full_option += option2[i]
                        if len_option_3 > i:
                            full_option += option3[i]
                        if len(option4) > i:
                            full_option += option4[i]
                    for i in range(0, len_encrypted_data):
                        if special_chars_as_spaces[i] == " ":
                            full_option = full_option[:i] + " " + full_option[i:]
                    if full_option == ok:
                        print(full_option)
                    full_option_words_list = full_option.split(' ')
                    for word in full_option_words_list:
                        if word in english_dictionary_tuple:
                            flag = True
                            count += 1
                    if flag:
                        if count // len(full_option_words_list) > 0.5:
                            print(full_option)
                    full_option = ""
                    flag = False
                    count = 0
                    attempt_number += 1
                    if attempt_number % 1000 == 0:
                        print(attempt_number)
    print(count)


if __name__ == '__main__':
    main()
