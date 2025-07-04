import ipaddress
import sys
import random

asia_ranges = [
    ipaddress.ip_network('104.16.0.0/13'),
    ipaddress.ip_network('104.24.0.0/14'),
    ipaddress.ip_network('141.101.64.0/18'),
    ipaddress.ip_network('162.158.0.0/15'),
    ipaddress.ip_network('188.114.96.0/20'),
]

def is_asia_ip(ip):
    return any(ip in net for net in asia_ranges)

ips = []

with open(sys.argv[1]) as f:
    for line in f:
        try:
            network = ipaddress.ip_network(line.strip())
            for ip in network.hosts():
                if is_asia_ip(ip):
                    ips.append(str(ip))
        except ValueError:
            continue

sample_size = min(1000, len(ips))
for ip in random.sample(ips, sample_size):
    print(ip)
