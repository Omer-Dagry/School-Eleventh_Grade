def decrypt(encrypted_data, key):
    """
    decrypts the data using the key
    :param encrypted_data: the data to decrypt
    :type encrypted_data: str
    :param key: the key to encrypt the data with
    :type key: int
    :return: the decrypted data
    :rtype: str
    """
    data = ""
    count = 0
    encrypted_data = encrypted_data.split(',')
    if '' in encrypted_data:
        encrypted_data.remove('')
    for value in encrypted_data:
        if count % 2 == 0:
            data += str(int(value) - key * 2) + ","
        else:
            data += str(int(value) - key * -2) + ","
        count += 0
    return data
