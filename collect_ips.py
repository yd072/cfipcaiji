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
    # 你可以添加更多的域名
]

# 检查 proxyip.txt 文件是否存在，如果存在则删除它
if os.path.exists('proxyip.txt'):
    os.remove('proxyip.txt')

# 创建一个文件来存储域名及其 IP 地址
with open('proxyip.txt', 'w') as file:
    for domain in domains:
        try:
            print(f"正在解析域名: {domain}")
            # 使用 socket 获取 IP 地址
            ip_address = socket.gethostbyname(domain)
            print(f"域名 {domain} 解析为 IP 地址: {ip_address}")

            # 使用 ipinfo.io 获取 IP 地址的国家信息
            response = requests.get(f'https://ipinfo.io/{ip_address}/json')
            
            # 打印响应状态码和内容
            print(f"请求 ipinfo.io 返回的状态码: {response.status_code}")
            print(f"响应内容: {response.text}")

            # 如果响应失败，检查返回状态码
            if response.status_code != 200:
                print(f"请求失败，状态码: {response.status_code}，无法获取 {ip_address} 的国家信息")
                file.write(f"{ip_address} #无法获取国家信息\n")
                continue

            # 解析响应的 JSON 数据
            data = response.json()
            country_code = data.get('country', 'Unknown')  # 获取国家代码
            print(f"IP 地址 {ip_address} 对应的国家是: {country_code}")

            # 写入 IP 地址和国家代码，格式：IP 地址 #国家简称
            file.write(f'{ip_address} #{country_code}\n')  # 格式: IP 地址 #国家简称
            
        except socket.gaierror as e:
            # 如果解析失败，打印错误并跳过
            print(f"无法解析域名 {domain}: {e}")
            continue
        except requests.exceptions.RequestException as e:
            # 如果请求 IP 信息失败
            print(f"请求 {domain} 的 IP 信息失败: {e}")
            file.write(f"错误: {domain} #无法请求国家信息\n")
            continue

print('域名解析的 IP 地址和国家代码已保存到 proxyip.txt 文件中。')
