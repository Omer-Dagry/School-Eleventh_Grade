"""
 Author: Omer Dagry
 Date: 5/02/2022

 6.19
"""
import scapy.all as scapy
from scapy.layers.inet import IP, TCP

COMMUNICATE_WITH = "10.100.102.18"   # The IP Address of the device you want to communicate with
SRC = "10.100.102.15"


def main():
    open_ports = []
    for port in range(20, 1025):
        synack = scapy.sr1((IP(src=SRC, dst=COMMUNICATE_WITH) /
                            TCP(dport=port, flags='S', seq=1000)), verbose=0, timeout=5)
        if TCP in synack and synack[TCP].flags & 0x02 and synack[TCP].flags & 0x10:
            open_ports.append(port)
    print(open_ports)


if __name__ == '__main__':
    main()