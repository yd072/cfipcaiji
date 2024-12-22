import socket
import os
import requests
import time

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
    # 你可以添加更多域名
]

# 检查 proxyip.txt 文件是否存在，如果存在则删除它
file_path = 'proxyip.txt'

# 打印路径，以确认 GitHub Actions 工作目录
print(f"当前工作目录：{os.getcwd()}")

# 检查并删除文件
if os.path.exists(file_path):
    print(f"删除现有文件 {file_path}")
    os.remove(file_path)

# 创建一个文件来存储域名及其 IP 地址
with open(file_path, 'w') as file:
    for domain in domains:
        try:
            # 使用 socket 获取 IP 地址
            ip_address = socket.gethostbyname(domain)
            print(f"解析 {domain} 得到 IP 地址: {ip_address}")
            
            # 使用 ipinfo.io 获取 IP 地址的国家信息
            try:
                response = requests.get(f'https://ipinfo.io/{ip_address}/json', timeout=10)
                response.raise_for_status()  # 如果响应状态码不是 200，将抛出异常

                data = response.json()
                country_code = data.get('country', 'Unknown')  # 获取国家代码
                
                # 写入 IP 地址和国家代码，格式：IP 地址 #国家简称
                file.write(f'{ip_address} #{country_code}\n')
                print(f'{ip_address} #{country_code}')  # 控制台输出：IP 地址 #国家简称
            except requests.exceptions.RequestException as e:
                # 请求失败的错误处理
                print(f"请求错误 {domain} (IP: {ip_address}): {e}")
                file.write(f"{ip_address} #Error retrieving country\n")
            
        except socket.gaierror as e:
            # 如果解析失败，打印错误并跳过
            print(f"无法解析域名 {domain}: {e}")
            continue

        # 防止请求过快，可以在每个域名之间添加延迟，避免频繁请求被限制
        time.sleep(1)

print(f'域名解析的 IP 地址和国家代码已保存到 {file_path} 文件中。')
