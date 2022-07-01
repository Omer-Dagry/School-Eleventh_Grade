"""
 Author: Omer Dagry
 Date: 5/02/2022

 6.13
"""
import logging
import os
import sys
import scapy.all as scapy
from scapy.layers.inet import IP, UDP

# logging
LOG_FORMAT = "%(levelname)s | %(asctime)s | %(processName)s | %(message)s"
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = LOG_DIR + "/s613.log"

chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()+="":><./\\][{}-_|?,~`"

COMMUNICATE_WITH = "10.100.102.45"  # The IP Address of the device you want to communicate with


def my_filter(packet):
    return (UDP in packet) and (IP in packet) and (packet[IP].src == COMMUNICATE_WITH)


def snifff():
    while True:
        sniffed = scapy.sniff(lfilter=my_filter, count=1)
        printt(sniffed)


def printt(packets):
    msg = ""
    for packet in packets:
        if chr(int(packet[UDP].dport)) in chars:
            msg += chr(int(packet[UDP].dport))
            logging.info("sniffed: %s" % msg)
    sys.stdout.write(msg)
    sys.stdout.flush()


def main():
    if not os.path.isdir(LOG_DIR):
        os.makedirs(LOG_DIR)
    logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)
    snifff()


if __name__ == '__main__':
    main()
