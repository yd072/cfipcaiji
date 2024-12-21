import socket
import os

# 目标域名列表
domains = [
    'proxyip.fxxk.dedyn.io',  # 你想解析的域名
    # 可以添加更多域名
]

# 检查 ip.txt 文件是否存在，如果存在则删除它
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

# 创建一个文件来存储域名及其 IP 地址
try:
    with open('ip.txt', 'w') as file:
        for domain in domains:
            try:
                # 使用 socket 获取 IP 地址
                ip_address = socket.gethostbyname(domain)
                file.write(f'{domain}: {ip_address}\n')
                print(f'{domain}: {ip_address}')
            except socket.gaierror as e:
                # 如果解析失败，记录错误信息
                file.write(f'{domain}: Failed to resolve ({e})\n')
                print(f'{domain}: Failed to resolve ({e})')

    print('域名解析的 IP 地址已保存到 ip.txt 文件中。')

except Exception as e:
    print(f"发生错误：{e}")
