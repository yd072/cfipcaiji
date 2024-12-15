import requests
from bs4 import BeautifulSoup
import re
import os

# 目标URL列表
urls = [
    'https://cf.090227.xyz',
    'https://ip.164746.xyz'
]

# 正则表达式用于匹配IP地址
ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'

# 删除旧的ip.txt文件
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

# 保存IP地址到文件
unique_ips = set()

for url in urls:
    try:
        # 获取网页内容
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        # 如果网页使用特殊编码，可以设置编码格式
        response.encoding = response.apparent_encoding

        # 解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取网页中的所有文本并搜索IP
        text_content = soup.get_text()
        ip_matches = re.findall(ip_pattern, text_content)
        
        # 添加到集合去重
        unique_ips.update(ip_matches)
    except requests.RequestException as e:
        print(f"请求失败 {url}: {e}")

# 将IP地址写入文件
with open('ip.txt', 'w') as file:
    for ip in sorted(unique_ips):  # 按字典序排序便于查看
        file.write(ip + '\n')

print(f"已从 {len(urls)} 个URL中提取IP地址，保存到 ip.txt 文件。")
