"""
Deja Vu exercise
written by Nir Dweck
Description: reads a number from the user, prints its digits and their sum
Date: 12/7/2016
"""
ENTER_NUM = 'Please insert a 5-digits number::\n'
NUM_ENTERED = 'You entered the number: %s'
DIGIT_LIST = 'The digits of this number are: %s'
SUM_OF_DIGITS = 'The sum of the digits is: %d'
INPUT_LEN = 5


def validate_input(num):
    """
    validates the passed number (which should be of type string).
    The input should be a valid 5 digit number (as a string)
    :param num: a string containing the number to validate
    :return: True if the number is a 5 digits number, False if not
    :rtype: boolean
    """
    return (type(num) is str) and (len(num) == INPUT_LEN) and (num.isdigit())


def get_user_input():
    """
    receive the user input. verifies that the user input is a 5 digit number
    :return: the user input - a 5 digit number
    :rtype str
    """
    valid = False
    user_input = ''
    while not valid:
        user_input = input(ENTER_NUM)
        valid = validate_input(user_input)

    return user_input


def jan_valjan():
    """
    perform the entire task
    1) get a number from the user
    2) print the number the user entered
    3) print each digit of the number the user inserted
    4) print the sum of the digits
    :return: None
    """
    user_input = get_user_input()
    print(NUM_ENTERED % user_input)
    user_input_list = list(user_input)
    print(DIGIT_LIST % ",".join([x for x in user_input_list]))
    num_list = [int(num) for num in user_input_list]
    print(SUM_OF_DIGITS % sum(num_list))


if __name__ == "__main__":
    assert not validate_input('helpm')
    assert not validate_input('1234')
    assert not validate_input('')
    assert not validate_input(12)
    assert not validate_input(12345)
    assert not validate_input('-34543')
    assert not validate_input('-3454')
    assert not validate_input('5.2545')
    assert not validate_input('5.254')
    assert validate_input('34543')

    jan_valjan()
