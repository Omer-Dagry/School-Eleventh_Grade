import logging
import os
import scapy.all as scapy
from scapy.layers.dns import DNS, DNSQR
from scapy.layers.inet import IP, UDP

# logging
LOG_FORMAT = "%(levelname)s | %(asctime)s | %(processName)s | %(message)s"
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = LOG_DIR + "/612.log"


def get_ip(answers, num_answers, qtype):
    for answer in range(0, num_answers):
        if answers[answer].type == qtype:
            return answers[answer].rdata


def main():
    if not os.path.isdir(LOG_DIR):
        os.makedirs(LOG_DIR)
    logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)
    hostname = input("nslookup ")
    logging.info("Hostname = %s" % hostname)
    dns_req = IP(dst='8.8.8.8') / UDP(dport=53) / DNS(qdcount=1, rd=1) / DNSQR(qname=hostname)
    response = scapy.sr1(dns_req, verbose=0)
    logging.info(response.show(dump=True))
    answers = response.an
    ip = ""
    if answers is not None:
        ip = get_ip(answers, response.ancount, dns_req.qtype)
    if ip is not None:
        logging.info("The IP address of %s is %s" % (hostname, ip))
        print("The IP address of %s is %s" % (hostname, ip))
    else:
        logging.info("IP not found")
        print("Can't find the IP address of %s" % hostname)


if __name__ == '__main__':
    main()
