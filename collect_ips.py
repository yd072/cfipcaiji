import requests
from bs4 import BeautifulSoup
import re

# 目标URL列表
urls = ['https://cf.090227.xyz', 'https://ip.164746.xyz']

# 正则表达式匹配IP地址和网速
ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
speed_pattern = r'(\d+(\.\d+)?)\s?(M|G)bps'  # 匹配网速，例如"10Mbps"或"1Gbps"

# 保存结果
ip_speed_list = []

for url in urls:
    try:
        # 发送HTTP请求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 假设IP和网速信息在<tr>标签中
        rows = soup.find_all('tr')
        for row in rows:
            text_content = row.get_text()
            ip_matches = re.findall(ip_pattern, text_content)
            speed_matches = re.findall(speed_pattern, text_content)

            if ip_matches and speed_matches:
                ip = ip_matches[0]
                speed, _, unit = speed_matches[0]
                speed_value = float(speed) * (1024 if unit == 'G' else 1)  # Gbps转换为Mbps

                if speed_value >= 10:  # 过滤网速大于等于10Mbps的IP
                    ip_speed_list.append((ip, speed_value))

    except requests.RequestException as e:
        print(f"请求失败 {url}: {e}")

# 将结果保存到文件
with open('ip_speed.txt', 'w') as file:
    for ip, speed in sorted(ip_speed_list, key=lambda x: x[1], reverse=True):  # 按网速降序排序
        file.write(f"{ip} - {speed} Mbps\n")

print(f"完成，提取到 {len(ip_speed_list)} 个网速大于等于10M的IP，结果保存在 ip_speed.txt 中。")
