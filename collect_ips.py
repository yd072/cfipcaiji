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
            response.raise_for_status()

            # 打印HTML内容以调试（可以注释掉）
            print(f"调试HTML内容：{url}")
            print(response.text[:1000])  # 打印部分HTML内容

            # 解析HTML内容
            soup = BeautifulSoup(response.text, 'html.parser')

            # 尝试解析不同的结构
            # 1. 提取所有文本
            all_text = soup.get_text()
            ip_matches = re.findall(ip_pattern, all_text)

            # 2. 如果IP不在纯文本中，尝试通过标签提取
            if not ip_matches:
                elements = soup.find_all('tr')  # 假设IP地址在<tr>标签中
                for element in elements:
                    text_content = element.get_text()
                    ip_matches.extend(re.findall(ip_pattern, text_content))

            # 3. 保存到文件
            if ip_matches:
                for ip in ip_matches:
                    file.write(ip + '\n')
                print(f"成功提取 {len(ip_matches)} 个IP来自 {url}")
            else:
                print(f"未找到IP地址: {url}")

        except requests.RequestException as e:
            print(f"请求失败 {url}: {e}")

print('IP地址已保存到 ip.txt 文件中。')
