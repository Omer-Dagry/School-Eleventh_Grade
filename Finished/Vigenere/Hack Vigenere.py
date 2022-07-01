from math import ceil
from collections import Counter
from test import english_dictionary_list

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
        return [4]  # possible_key_lengths
    else:
        key_lengths.sort()
        return [4]  # key_lengths


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


def best_words(all_options):
    all_options_grades = []
    for list in all_options:
        all_options_grades.append([])
        for option in list:
            list_string = "".join(option)
            vp = Counter(list_string).most_common()
            sorted_string = ""
            for item in vp:
                sorted_string += item[0]
            count = 0
            score = 0
            for i in range(0, len(sorted_string)):
                for char in COMMON_LETTERS:
                    if char == sorted_string[i]:
                        score += 1
                count += 1
                if count == 6:
                    break
            # count = 0
            # for i in range(-1, (len(sorted_string) * -1) - 1, -1):
            #     for char in LEAST_COMMON_LETTERS:
            #         if char == sorted_string[i]:
            #             score += 1
            #     count += 1
            #     if count == 6:
            #         break
            all_options_grades[all_options.index(list)].append([option, score])
    print(all_options_grades)
    best_words0 = []
    for list in all_options_grades:
        max = list[all_options_grades.index(list)][1]
        max_words = [list[all_options_grades.index(list)][1]]
        for option in list:
            if option[1] > max:
                max = option[1]
                max_words.append(option[0])
                i = 0
                while i < len(max_words):
                    del max_words[i]
                    i += 1
            if option[1] == max:
                max = option[1]
                max_words.append(option[0])
        best_words0.append([max_words])
    return best_words0


def main():
    encrypted_data_input = "csastpkvsiqutgqucsastpiuaqjb".lower()  # input("please enter data to decrypt").lower()
    encrypted_data = ""
    for char in encrypted_data_input:
        if char in "abcdefghijklmnopqrstuvwxyz":
            encrypted_data += char
    possible_key_lengths = get_key_lengths(encrypted_data)  # get duplicates and their place
    print(possible_key_lengths)
    # get the chars that are encrypted with the same char in key
    same_char_list = same_char_encryption(encrypted_data, possible_key_lengths[0])
    print(same_char_list)
    all_options = get_all_options(same_char_list)
    print(all_options)
    # best_words0 = best_words(all_options)
    # print(best_words0)
    list_string_1 = all_options[0]
    list_string_2 = all_options[1]
    list_string_3 = all_options[2]
    list_string_4 = all_options[3]
    full_option = ""
    count = 0
    if "crypto" in english_dictionary_list:
        print("ok")
    else:
        print("not ok")
    for option1 in list_string_1:
        for option2 in list_string_2:
            for option3 in list_string_3:
                for option4 in list_string_4:
                    for i in range(0, len(option1)):
                        full_option += option1[i] + option2[i] + option3[i] + option4[i]
                    if full_option[dup1[0]:dup1[1]] in english_dictionary_list:
                        print(full_option)
                        count += 1
                    full_option = ""
    print(count)


if __name__ == '__main__':
    main()
