import requests
from bs4 import BeautifulSoup
import re

# 目标URL列表
urls = ['https://cf.090227.xyz', 'https://ip.164746.xyz']

# 正则表达式匹配IP地址
ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'  # 精确匹配IPv4地址

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

        # 调试抓取的HTML内容（可选）
        print(f"抓取的HTML内容 (前500字符)：\n{response.text[:500]}")

        # 直接匹配文本中的IP地址
        ip_matches = []
        elements = soup.find_all(text=re.compile(ip_pattern))
        for element in elements:
            ip_matches.extend(re.findall(ip_pattern, element))

        if ip_matches:
            print(f"提取成功：{len(ip_matches)} 个IP来自 {url}")
            return ip_matches
        else:
            print(f"未找到IP地址：{url}")
            return []

    except requests.RequestException as e:
        print(f"请求失败 {url}: {e}")
        return []

# 主程序
def main():
    ip_addresses = []
    for url in urls:
        ip_addresses.extend(extract_ips_from_url(url))

    # 保存IP地址到文件
    with open('ip.txt', 'w') as file:
        for ip in ip_addresses:
            file.write(ip + '\n')

    print('IP地址已保存到 ip.txt 文件中。')

if __name__ == "__main__":
    main()
