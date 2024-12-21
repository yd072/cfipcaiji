import socket

# 目标域名列表
domains = [
    'proxyip.fxxk.dedyn.io'
  
]

# 检查ip.txt文件是否存在，如果存在则删除它
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

# 创建一个文件来存储域名及其IP地址
with open('ip.txt', 'w') as file:
    for domain in domains:
        try:
            # 使用socket获取IP地址
            ip_address = socket.gethostbyname(domain)
            file.write(f'{domain}: {ip_address}\n')
            print(f'{domain}: {ip_address}')
        except socket.gaierror:
            # 如果解析失败，记录错误信息
            file.write(f'{domain}: Failed to resolve\n')
            print(f'{domain}: Failed to resolve')

print('域名解析的IP地址已保存到ip.txt文件中。')
