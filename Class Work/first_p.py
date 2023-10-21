"""
Author: Omer Dagry
Program name: my first python program
Description: prints hello to the user and displyes the program arguments
Date: 10.9.2021
"""
import sys


def main():
    name = input("Please enter your name: ")
    print('hello %s' % name)
    print(sys.argv)


if __name__ == '__main__':
    main()
