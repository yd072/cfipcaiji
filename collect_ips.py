import requests
from bs4 import BeautifulSoup
import re
import os

# 目标URL列表
urls = ['https://cf.090227.xyz', 'https://ip.164746.xyz']

# 正则表达式匹配IP地址
ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'

# 删除旧的ip.txt文件
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

# 保存IP地址到文件
with open('ip.txt', 'w') as file:
    for url in urls:
        try:
            # 设置请求头，避免被反爬虫检测
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36'
            }

            # 获取网页内容
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # 检查请求是否成功
            
            # 解析HTML内容
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取网页中的所有文本内容
            all_text = soup.get_text()

            # 查找符合IP格式的内容
            ip_matches = re.findall(ip_pattern, all_text)
            if ip_matches:
                for ip in ip_matches:
                    file.write(ip + '\n')
                print(f"提取成功: {len(ip_matches)} 个IP来自 {url}")
            else:
                print(f"未找到IP地址: {url}")

        except requests.RequestException as e:
            print(f"请求失败 {url}: {e}")

print('IP地址已保存到 ip.txt 文件中。')
