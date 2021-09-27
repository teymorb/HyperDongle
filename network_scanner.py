import scapy.all as scapy


def scan(ip):  # Function to scan an IP or range of IPs (of the form X.X.X.X/CIDR) for available devices
    arp_req_frame = scapy.ARP(pdst = ip)

    broadcast_ether_frame = scapy.Ether(dst = "ff:ff:ff:ff:ff:ff")

    broadcast_ether_arp_req_frame = broadcast_ether_frame / arp_req_frame

    answered_list = scapy.srp(broadcast_ether_arp_req_frame, timeout=1, verbose=False)[0]
    result = []
    for i in range(0, len(answered_list)):
        client_dict = {"ip": answered_list[i][1].psrc, "mac": answered_list[i][1].hwsrc}
        result.append(client_dict)

    return result

if __name__ == '__main__':
    res = scan("192.168.1.0/24")

    found = ["IP: "+ r['ip'] + (" " * (15 - len(r['ip']))) + "| MAC: " + r['mac'] for r in res]

    print('\n'.join(found))