import requests
from bs4 import BeautifulSoup
import re
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# 正则表达式匹配IP地址
ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
speed_pattern = r'(\d+(\.\d+)?)\s?(M|G)bps'  # 匹配网速，以M或G为单位

# 目标URL列表
urls = [
    'https://cf.090227.xyz',
    'https://ip.164746.xyz'
]

# 删除旧的ip.txt文件
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

# 保存IP地址的集合（去重）
unique_ips = set()


# 静态页面抓取函数（过滤网速大于等于10M的IP）
def fetch_static_ips(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # 解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取网页中的所有文本
        rows = soup.find_all('tr')

        ip_speed_pairs = []
        for row in rows:
            # 假设每行中包含IP和网速信息
            text_content = row.get_text()
            ip_matches = re.findall(ip_pattern, text_content)
            speed_matches = re.findall(speed_pattern, text_content)

            if ip_matches and speed_matches:
                ip = ip_matches[0]
                speed = speed_matches[0][0]  # 获取网速
                # 将网速转换为数值并判断是否大于等于10M
                if 'G' in speed:
                    speed_value = float(speed.replace('G', '')) * 1024  # Gbps转换为Mbps
                else:
                    speed_value = float(speed.replace('M', ''))

                if speed_value >= 10:
                    ip_speed_pairs.append((ip, speed_value))

        return ip_speed_pairs
    except requests.RequestException as e:
        print(f"请求失败 {url}: {e}")
        return []


# 动态页面抓取函数（过滤网速大于等于10M的IP）
def fetch_dynamic_ips(url):
    try:
        # 配置ChromeDriver路径
        driver_path = '/path/to/chromedriver'  # 替换为实际的chromedriver路径

        # 启动浏览器
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # 无界面模式
        options.add_argument('--disable-gpu')  # 禁用GPU加速
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)

        # 打开目标页面
        driver.get(url)

        # 获取页面HTML内容
        page_source = driver.page_source

        # 提取IP和网速信息
        rows = driver.find_elements(By.TAG_NAME, 'tr')
        
        ip_speed_pairs = []
        for row in rows:
            text_content = row.text
            ip_matches = re.findall(ip_pattern, text_content)
            speed_matches = re.findall(speed_pattern, text_content)

            if ip_matches and speed_matches:
                ip = ip_matches[0]
                speed = speed_matches[0][0]  # 获取网速
                # 将网速转换为数值并判断是否大于等于10M
                if 'G' in speed:
                    speed_value = float(speed.replace('G', '')) * 1024  # Gbps转换为Mbps
                else:
                    speed_value = float(speed.replace('M', ''))

                if speed_value >= 10:
                    ip_speed_pairs.append((ip, speed_value))

        # 关闭浏览器
        driver.quit()

        return ip_speed_pairs
    except Exception as e:
        print(f"动态抓取失败 {url}: {e}")
        return []


# 主逻辑
for url in urls:
    # 尝试静态抓取
    print(f"尝试从静态页面抓取: {url}")
    static_ips = fetch_static_ips(url)

    if static_ips:
        unique_ips.update(static_ips)
    else:
        # 如果静态抓取失败，尝试动态抓取
        print(f"静态抓取失败，尝试从动态页面抓取: {url}")
        dynamic_ips = fetch_dynamic_ips(url)
        unique_ips.update(dynamic_ips)

# 将IP地址写入文件
with open('ip.txt', 'w') as file:
    for ip, speed in sorted(unique_ips, key=lambda x: x[1], reverse=True):  # 按网速降序排序
        file.write(f"{ip} - {speed} Mbps\n")

print(f"已从 {len(urls)} 个URL中提取网速大于等于10M的IP地址，保存到 ip.txt 文件。")
