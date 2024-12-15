import requests
from bs4 import BeautifulSoup
import re
import os

# 目标URL列表
urls = ['https://cf.090227.xyz',
        'https://ip.164746.xyz']

# 正则表达式用于匹配IP地址
ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'

# 删除旧的ip.txt文件
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

# 保存IP地址到文件
with open('ip.txt', 'w') as file:
    for url in urls:
        try:
            # 获取网页内容
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # 解析HTML内容
            soup = BeautifulSoup(response.text, 'html.parser')
            elements = soup.find_all('tr')  # 根据网页结构调整
            
            # 提取IP地址并写入文件
            for element in elements:
                element_text = element.get_text()
                ip_matches = re.findall(ip_pattern, element_text)
                for ip in ip_matches:
                    file.write(ip + '\n')
        except requests.RequestException as e:
            print(f"请求失败 {url}: {e}")

print('IP地址已保存到ip.txt文件中。')
