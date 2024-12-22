import socket
import os
import requests

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
if os.path.exists('proxyip.txt'):
    os.remove('proxyip.txt')

# 创建一个文件来存储域名及其 IP 地址
try:
    with open('proxyip.txt', 'w') as file:
        for domain in domains:
            try:
                # 使用 socket 获取 IP 地址
                ip_address = socket.gethostbyname(domain)
                print(f"解析 {domain} 得到 IP 地址: {ip_address}")

                # 使用 ipinfo.io 获取 IP 地址的国家信息
                response = requests.get(f'https://ipinfo.io/{ip_address}/json')
                
                # 检查是否成功获取数据
                if response.status_code == 200:
                    data = response.json()
                    country_code = data.get('country', 'Unknown')  # 获取国家代码
                    # 写入 IP 地址和国家代码，格式：IP 地址 #国家简称
                    file.write(f'{ip_address} #{country_code}\n')
                    print(f'{ip_address} #{country_code}')  # 控制台输出：IP 地址 #国家简称
                else:
                    print(f"请求失败，状态码: {response.status_code}，无法获取 {ip_address} 的国家信息")
                    file.write(f"{ip_address} #无法获取国家信息\n")

            except socket.gaierror as e:
                # 如果解析失败，打印错误并跳过
                print(f"无法解析域名 {domain}: {e}")
                continue
            except requests.exceptions.RequestException as e:
                # 如果请求 IP 信息失败
                print(f"请求 {domain} 的 IP 信息失败: {e}")
                file.write(f"{domain} #请求错误\n")
                continue

    print('域名解析的 IP 地址和国家代码已保存到 proxyip.txt 文件中。')

except Exception as e:
    print(f"发生了未知错误: {e}")
