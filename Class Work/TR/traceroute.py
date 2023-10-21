from math import ceil
import scapy.all as scapy
from scapy.layers.dns import DNS, DNSQR
from scapy.layers.inet import IP, ICMP, UDP
# cryptography==36.0.2


def nslookup(hostname):
    # sends an dns request for hostname
    dns_req = IP(dst='8.8.8.8') / UDP(dport=53) / DNS(qdcount=1, rd=1) / DNSQR(qname=hostname)
    response = scapy.sr1(dns_req, verbose=0)
    answers = response.an  # gets all the answers from the response
    if answers is not None:  # checks that there are actually answers
        for answer in range(0, response.ancount):  # goes through all the answers until found dns response
            if answers[answer].type == dns_req.qtype:
                print("Target IP Address: '%s'" % answers[answer].rdata)
                return answers[answer].rdata
    return None


def traceroute(hostname):
    # if hostname isn't an ip address it will try to get the ip address of hostname and print it
    if not (hostname.count(".") == 3 and
            [0 <= int(value) <= 255 for value in hostname.split(".")] == [True for i in range(4)]):
        nslookup(hostname)
    stop = False
    # packet ttl (time to live) is 1 for the first time
    # the ttl is increases by 1 until the response is from hostname
    ttl = 1
    print("\n Hop Number | Response Time (ms) |    IP Address    |\n")
    # loop until getting a response from hostname
    while not stop:
        # send ping to hostname with ttl
        packet = IP(dst=hostname, ttl=ttl) / ICMP()
        replay = scapy.sr1(packet, verbose=0, timeout=3)
        if replay is not None:
            r_time = float("%.5f" % (replay.time - packet.sent_time))  # response time
            r_addr = replay[IP].src  # response ip address
        else:
            r_time = "*"
            r_addr = "Request timed out."
        # if response is from hostname
        if replay is not None and ICMP in replay and IP in replay and replay[ICMP].type == 0:
            print()
            print(" " * (6 - ceil(len(str(ttl)) / 2)) + str(ttl) + " " * (6 - (len(str(ttl)) // 2)) + "|" +
                  " " * (10 - ceil(len(str(r_time)) / 2)) + str(r_time) + " " * (10 - (len(str(r_time)) // 2)) + "|" +
                  " " * (9 - ceil(len(str(r_addr)) / 2)) + str(r_addr) + " " * (9 - (len(str(r_addr)) // 2)) + "|\n")
            print("Trace Complete. (%d Hops)" % ttl)
            # print("\n" + "response time {:.2f}".format(replay.time - packet.sent_time)
            #       + " ms | address", replay[IP].src + "\nTrace Complete.")
            stop = True
        else:
            print(" " * (6 - ceil(len(str(ttl)) / 2)) + str(ttl) + " " * (6 - (len(str(ttl)) // 2)) + "|" +
                  " " * (10 - ceil(len(str(r_time)) / 2)) + str(r_time) + " " * (10 - (len(str(r_time)) // 2)) + "|" +
                  " " * (9 - ceil(len(str(r_addr)) / 2)) + str(r_addr) + " " * (9 - (len(str(r_addr)) // 2)) + "|")
            # print(str(ttl - 1) + ") response time {:.2f}".format(replay.time - packet.sent_time)
            #       + " ms | address", replay[IP].src)
            ttl += 1


def main():
    hostname = input("Traceroute To: ")
    traceroute(hostname)


if __name__ == "__main__":
    main()
