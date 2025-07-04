import ipaddress
import sys

asia_ranges = [
    ipaddress.ip_network('104.16.0.0/13'),   # 包含部分 HK/SG
    ipaddress.ip_network('162.158.0.0/15'),
    ipaddress.ip_network('188.114.96.0/20'),
    ipaddress.ip_network('141.101.64.0/18'),
    ipaddress.ip_network('203.0.113.0/24'),  # 示例网段，可替换
]

def is_asia_ip(ip):
    for net in asia_ranges:
        if ip in net:
            return True
    return False

with open(sys.argv[1]) as f:
    for line in f:
        network = ipaddress.ip_network(line.strip())
        for ip in network.hosts():
            if is_asia_ip(ip):
                print(str(ip))
