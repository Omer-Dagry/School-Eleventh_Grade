import scapy.all as scapy
from scapy.layers.inet import IP, ICMP


def main():
    hostname = input("Traceroute ")
    flag = True
    ttl = 1
    while flag:
        packet = IP(dst=hostname, ttl=ttl) / ICMP()
        replay = scapy.sr1(packet, verbose=0)
        if ICMP in replay and IP in replay and replay[ICMP].type == 0:
            print("\n" + "response time {:.2f}".format(replay.time - packet.sent_time)
                  + " ms | address", replay[IP].src + "\nTrace Complete.")
            flag = False
        else:
            ttl += 1
            print(str(ttl) + ") response time {:.2f}".format(replay.time - packet.sent_time)
                  + " ms | address", replay[IP].src)


if __name__ == "__main__":
    main()
