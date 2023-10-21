"""
 Author: Omer Dagry
 Date: 5/02/2022

 6.13
"""
import logging
import os
from time import sleep
import scapy.all as scapy
from scapy.layers.inet import IP, UDP

# logging
LOG_FORMAT = "%(levelname)s | %(asctime)s | %(processName)s | %(message)s"
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = LOG_DIR + "/c613.log"

COMMUNICATE_WITH = "10.100.102.23"  # The IP Address of the device you want to communicate with


def send_msg(port):
    scapy.send((IP(dst=COMMUNICATE_WITH) / UDP(dport=port)), verbose=0)
    sleep(0.1)


def main():
    if not os.path.isdir(LOG_DIR):
        os.makedirs(LOG_DIR)
    logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)
    msg = input("Please Enter A Msg: ")
    logging.info("The Msg: %s" % msg)
    for char in msg:
        send_msg(ord(char))


if __name__ == '__main__':
    main()
