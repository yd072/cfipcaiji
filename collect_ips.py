import socket
import os

# 目标域名列表
domains = [
    'proxyip.fxxk.dedyn.io',
    'proxyip.us.fxxk.dedyn.io',
    'proxyip.sg.fxxk.dedyn.io',
    'proxyip.jp.fxxk.dedyn.io',
    'proxyip.hk.fxxk.dedyn.io',
    'proxyip.aliyun.fxxk.dedyn.io',
    'proxyip.oracle.fxxk.dedyn.io',
    'proxyip.digitalocean.fxxk.dedyn.io',
    # 你想解析的域名
    # 你可以添加更多的域名
]

# 检查 ip.txt 文件是否存在，如果存在则删除它
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

# 创建一个文件来存储域名及其 IP 地址
with open('ip.txt', 'w') as file:
    for domain in domains:
        try:
            # 使用 socket 获取 IP 地址
            ip_address = socket.gethostbyname(domain)
            file.write(f'{ip_address}\n')  # 只写入 IP 地址
            print(ip_address)  # 控制台只显示 IP 地址
        except socket.gaierror:
            # 如果解析失败，不做任何操作，直接跳过
            continue

print('域名解析的 IP 地址已保存到 ip.txt 文件中。')
