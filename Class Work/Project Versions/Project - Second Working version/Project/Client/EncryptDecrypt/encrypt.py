def encrypt(data, key):
    """
    encrypts the data using the key
    :param data: the data to encrypt
    :type data: str
    :param key: the key to encrypt the data with
    :type key: int
    :return: the encrypted data
    :rtype: str
    """
    encrypted_data = ""
    count = 0
    data = data.split(',')
    if '' in data:
        data.remove('')
    for value in data:
        if count % 2 == 0:
            encrypted_data += str(int(value) + key * 2) + ","
        else:
            encrypted_data += str(int(value) + key * -2) + ","
        count += 0
    return encrypted_data
