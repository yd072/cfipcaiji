import requests
from bs4 import BeautifulSoup
import re

# 目标URL列表
urls = ['https://cf.090227.xyz', 'https://ip.164746.xyz']

# 正则表达式匹配IP地址
ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'  # 精确匹配IPv4地址

# 获取IP的国家简称
def get_ip_country(ip):
    try:
        # 使用 ip-api 查询国家代码
        response = requests.get(f"http://ip-api.com/json/{ip}")
        data = response.json()
        
        # 打印返回的调试数据
        print(f"IP {ip} 返回数据: {data}")
        
        # 如果查询成功，返回国家代码，否则返回 unknown
        if data.get('status') == 'success':
            country = data.get('countryCode', 'unknown')  # 获取国家代码
            return country.lower()  # 转小写
        else:
            print(f"IP {ip} 查询失败：{data.get('message', '未知错误')}")
            return "unknown"
    except Exception as e:
        print(f"无法获取 {ip} 的国家信息: {e}")
        return "unknown"

# 保存IP地址到文件
def extract_ips_from_url(url):
    try:
        # 设置请求头，避免被反爬虫检测
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36'
        }
        # 获取网页内容
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 如果请求失败，会抛出异常

        # 解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')

        # 打印抓取的HTML内容前500字符，用于调试
        print(f"抓取的HTML内容 (前500字符)：\n{response.text[:500]}")

        # 直接匹配文本中的IP地址
        ip_matches = set()  # 使用集合来自动去重
        elements = soup.find_all(text=re.compile(ip_pattern))
        for element in elements:
            ip_matches.update(re.findall(ip_pattern, element))  # 使用update方法添加IP，避免重复

        if ip_matches:
            print(f"提取成功：{len(ip_matches)} 个唯一IP来自 {url}")
            return ip_matches
        else:
            print(f"未找到IP地址：{url}")
            return set()

    except requests.RequestException as e:
        print(f"请求失败 {url}: {e}")
        return set()

# 主程序
def main():
    ip_addresses = set()  # 使用集合来保存所有IP地址，自动去重
    for url in urls:
        ip_addresses.update(extract_ips_from_url(url))  # 使用update方法添加IP，避免重复

    # 如果提取到的IP地址为空
    if ip_addresses:
        # 保存去重后的IP地址到文件，每个IP地址后面加上国家简称
        with open('ip.txt', 'w') as file:
            for ip in ip_addresses:
                country = get_ip_country(ip)  # 获取国家简称
                file.write(f"{ip}#{country}\n")  # 在每个IP地址后添加国家简称
        print('IP地址已保存到 ip.txt 文件中。')
    else:
        print('没有提取到任何IP地址。')

if __name__ == "__main__":
    main()
