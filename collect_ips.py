from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import re
import time

# 配置Chrome驱动路径
driver_path = '/path/to/chromedriver'  # 替换为你的chromedriver路径

# 设置浏览器选项
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 无头模式
options.add_argument('--disable-gpu')

# 初始化浏览器
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=options)

# 目标URL
url = 'https://cf.090227.xyz'

# 正则表达式匹配IP地址和网速
ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
speed_pattern = r'(\d+(\.\d+)?)\s?(M|G)bps'  # 匹配网速

# 保存符合条件的IP和网速
ip_speed_list = []

try:
    # 打开网页
    driver.get(url)
    time.sleep(5)  # 等待页面加载完成

    # 假设IP和网速在<tr>标签中
    rows = driver.find_elements(By.TAG_NAME, 'tr')
    for row in rows:
        text_content = row.text
        ip_matches = re.findall(ip_pattern, text_content)
        speed_matches = re.findall(speed_pattern, text_content)

        if ip_matches and speed_matches:
            ip = ip_matches[0]
            speed, _, unit = speed_matches[0]
            # 将网速转换为Mbps
            speed_value = float(speed) * (1024 if unit == 'G' else 1)

            if speed_value >= 10:  # 筛选网速≥10Mbps的IP
                ip_speed_list.append((ip, speed_value))

except Exception as e:
    print(f"动态抓取失败: {e}")

# 关闭浏览器
driver.quit()

# 将结果保存到文件
with open('ip_speed.txt', 'w') as file:
    for ip, speed in sorted(ip_speed_list, key=lambda x: x[1], reverse=True):  # 按网速降序排序
        file.write(f"{ip} - {speed} Mbps\n")

print(f"完成，提取到 {len(ip_speed_list)} 个网速大于等于10M的IP，结果保存在 ip_speed.txt 中。")
