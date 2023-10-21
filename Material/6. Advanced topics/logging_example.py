"""
Author: Nir Dweck
Date: 20/9/2017
Description: logging example over the lucky number example
"""
import logging
import os


LOG_FORMAT = '%(levelname)s | %(asctime)s | %(processName)s | %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = LOG_DIR + '/lucky.log'


def validate_input(user_input):
    """
    validate that the input is an int.
    :param user_input: the user input string
    :return: True if the input is valid, False if not
    """
    return user_input.isdigit()


def main():
    """
    main function
    """
    if not os.path.isdir(LOG_DIR):
        os.makedirs(LOG_DIR)
    logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)
    valid = False
    number = ''
    while not valid:
        number = input('please enter your lucky number:')
        logging.debug('user entered ' + number)
        valid = validate_input(number)
        if not valid:
            print('please enter only integer numbers')
            logging.warning('user input was identified as invalid')

    new_number = int(number) * 10
    print('your new lucky number is ' + str(new_number))
    logging.info('user lucky number was ' + str(new_number))


if __name__ == '__main__':
    assert validate_input('3')
    assert not validate_input('f')
    main()
