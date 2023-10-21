from EncryptDecrypt import encrypt, decrypt

data_to_encrypt = "108,111,103,105,110,35,64,63,35,50,35,64,63,35,117,115,101,114,95,110,97,109,101,35,64,63,35,112," \
                  "97,115,115,119,111,114,100,35,64,63,35,79,109,101,114,35,64,63,35,49,"
print(data_to_encrypt)
encrypted_data = encrypt(data_to_encrypt, 106)
print(encrypted_data)
data = decrypt(encrypted_data, 106)
print(data)
print(data == data_to_encrypt)
