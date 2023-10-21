from math import ceil
from collections import Counter
from english_dictionary_tuple import english_dictionary_tuple
from threading import Thread
from multiprocessing import Pool

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


def aaaa_to_zzzz(list_string_1, list_string_2, list_string_3, list_string_4, special_chars_as_spaces):
    print("aaaa_to_zzzz start")
    full_option = ""
    count = 0
    count2 = 0
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
                    for i in range(0, len(special_chars_as_spaces)):
                        if special_chars_as_spaces[i] == " ":
                            full_option = full_option[:i] + " " + full_option[i:]
                    full_option_words_list = full_option.split(' ')
                    for word in full_option_words_list:
                        if word in english_dictionary_tuple:
                            count += 1
                    if count / len(full_option_words_list) > 0.5:
                        print(full_option)
                    full_option = ""
                    count = 0
                    count2 += 1
                    print(count2)
    print("aaaa_to_zzzz done")


def zzzz_to_aaaa(list_string_1, list_string_2, list_string_3, list_string_4, special_chars_as_spaces):
    print("zzzz_to_aaaa start")
    full_option = ""
    count = 0
    count2 = 0
    flag = False
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
                    for i in range(0, len(special_chars_as_spaces)):
                        if special_chars_as_spaces[i] == " ":
                            full_option = full_option[:i] + " " + full_option[i:]
                    full_option_words_list = full_option.split(' ')
                    for word in full_option_words_list:
                        if word in english_dictionary_tuple:
                            flag = True
                            count += 1
                    if flag:
                        if count / len(full_option_words_list) > 0.5:
                            print(full_option)
                    flag = False
                    full_option = ""
                    count = 0
                    count2 += 1
                    if count2 % 1000 == 0:
                        print("zzzz_to_aaaa " + str(count2))
    print("zzzz_to_aaaa done")


def main():
    encrypted_data_input = "ooeh uqqq a ukpe ujhrf yds b fhas nltunh gjto wiq zat nrvff ey fxhrzqqe xjr lpqnee cw hft, euu orsu qi amn ey igu gscqdnqwhft, dne vkesg zat prtikqg ujdt tjh wpwod oqw hbxh gjxhn uq whf ekimf. rndg vhf idvf jhr b nltunh hpqg og thd wgovfv, zhjek svkwee jhr tq zemn whbv vhf yrumf qewgu wfcu aoawhjpj emuh; sp uke xcv amydyt edlmgg 'ljvwlf thd-skgioi-kopf.' rnf fdy igu mpvkes udie vr hft: 'fong, oiuvoe sgg-rjflnh-jroe, jhrf kv a qkhcf qi cbmh aof d bpvwlf qi wjph; tbmh tigp tp arus iuaofpoujhr, tjh it kol bpg wfcn, aof whfa zimn go igu gpqg. sfv ruu dhfpth iu ihtt jrt, bpg wigq ypw drf irioi, zamm qidgoy bpg qvkhtma dne fr npv uuo qif ujh pbvk, os aru ncb fbno aof erfcn tig eouvoe, bpg tigq ypwu gscqdnqwhft zimn jeu prtikqg; bpg wigq ypw jo jpwo igu rpqp, dpp'w fptjeu vr sba, 'jopf posplnh', cqd eqq't qghp jpwo fxhrz errogu bfhrrf aru eq lt. 'j yllm vdkf iuebv fasg,' vajf oiuvoe sgg-rjflnh-jroe vr hft poujhr, bpg gbxh hft kaof rn jv. whf iuaofpoujhr mkyee qxt jp whf yroe, jdlg c oebixe gtrm ujh vjnoahg, dne lxsu cv ljvwlf thd-skgioi-kopf hnuguee vke xqrd, b yrlg oht igu. rff-uiekqg-iqrd ekg npv nnpy zhbv d wjenee euebvxrf jh wbu, dne yds oqw au col bhuajf rf ikp. 'gpqg dba, oiuvoe sgg-rjflnh-jroe,' udie jh. 'ticqk zqx kjpglz, yrlg.' 'ykiujhr bydy tq hasnb, ljvwlf thd-skgioi-kopf?' 'wo na jrbpgmpvkes'u.' 'zhbv kawg bov irt jp bovt dpsqq?' 'cbmh aof ziog; betvhrecb wbu ealkqg-ecb, sp rros ulcl iuaofpoujhr ju wo icye tqpeujlnh iroe, vr mbmh hft vtsqqgft.' 'zhfth dpgv ypwu gscqdnqwhft oiwg, oiuvoe sgg-rjflnh-jroe?' 'c jopf tubtwes qi a mgdgvg iasvkes qq io vke  xqrd; igu hpwve tvdneu xnegu tig whsgh lbtje pcn-tsghs, ujh nvv-wrfgv asg mutv eemqz; ypw vusgoy nwvt lprw jv,' ueqnlee nltunh rff-uiekqg-iqrd.".lower()  # input("please enter data to decrypt").lower()
    (encrypted_data, special_chars, special_chars_as_spaces) = extract_spaces(encrypted_data_input)
    # possible_key_lengths = get_key_lengths(encrypted_data)  # get duplicates and their place
    # print(possible_key_lengths)
    # get the chars that are encrypted with the same char in key
    same_char_list = same_char_encryption(encrypted_data, 4)
    print(len(same_char_list), " ", same_char_list)
    all_options = get_all_options(same_char_list)
    print(len(all_options), " ", all_options)
    print("start")
    list_string_1_reversed = []
    for item in all_options[0]:
        list_string_1_reversed.append(item)
    list_string_1_reversed.reverse()
    list_string_1 = all_options[0]
    list_string_2_reversed = []
    for item in all_options[1]:
        list_string_2_reversed.append(item)
    list_string_2_reversed.reverse()
    list_string_2 = all_options[1]
    list_string_3_reversed = []
    for item in all_options[2]:
        list_string_3_reversed.append(item)
    list_string_3_reversed.reverse()
    list_string_3 = all_options[1]
    list_string_4_reversed = []
    for item in all_options[3]:
        list_string_4_reversed.append(item)
    list_string_4_reversed.reverse()
    list_string_4 = all_options[1]
    print("done")
    ok = "one day her mother said to her come little red riding hood here is a piece of cake and a bottle of wine take them to your grandmother she is ill and weak and they will do her good set out before it gets hot and when you are going walk nicely and quietly and do not run off the path or you may fall and break the bottle and then your grandmother will get nothing and when you go into her room don t forget to say good morning and"
    ok_list = ok.split(' ')
    for word in ok_list:
        if word not in english_dictionary_tuple:
            print(word)
    a_to_zThread = Thread(target=aaaa_to_zzzz,
                          args=(list_string_1, list_string_2,list_string_3, list_string_4, special_chars_as_spaces))
    z_to_aThread = Thread(target=zzzz_to_aaaa,
                          args=(list_string_1_reversed, list_string_2_reversed,
                                list_string_3_reversed, list_string_4_reversed, special_chars_as_spaces))
    a_to_zThread.daemon = True
    z_to_aThread.daemon = True
    a_to_zThread.start()
    # z_to_aThread.start()
    


if __name__ == '__main__':
    main()
