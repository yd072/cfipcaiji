import requests
from bs4 import BeautifulSoup
import re

# 目标URL列表
urls = ['https://cf.090227.xyz', 'https://ip.164746.xyz','https://stock.hostmonit.com/CloudFlareYes']

# 正则表达式匹配IP地址
ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'

# 保存IP地址到文件
with open('ip.txt', 'w') as file:
    for url in urls:
        try:
            # 设置请求头，避免被反爬虫检测
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # 解析HTML内容
            soup = BeautifulSoup(response.text, 'html.parser')

            # 调整解析逻辑，根据实际结构修改这里
            elements = soup.find_all(text=re.compile(ip_pattern))  # 直接搜索包含IP的文本
            for element in elements:
                ip_matches = re.findall(ip_pattern, element)
                for ip in ip_matches:
                    file.write(ip + '\n')

        except requests.RequestException as e:
            print(f"请求失败 {url}: {e}")

print('IP地址已保存到 ip.txt 文件中。')
