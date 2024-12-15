from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import re
import time

# 配置Chrome驱动路径
driver_path = '/path/to/chromedriver'  # 替换为实际的chromedriver路径

# 设置Chrome浏览器选项
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 无头模式，不显示浏览器界面
options.add_argument('--disable-gpu')  # 禁用GPU加速

# 启动浏览器
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=options)

# 目标URL
url = 'https://cf.090227.xyz'

# 打开网页
driver.get(url)

# 等待页面加载
time.sleep(5)  # 根据实际情况调整等待时间

# 获取网页的HTML内容
page_source = driver.page_source

# 正则表达式匹配IP地址
ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
speed_pattern = r'(\d+(\.\d+)?)\s?(M|G)bps'  # 匹配网速，以M或G为单位

# 提取IP和网速信息
ip_speed_pairs = []
rows = driver.find_elements(By.TAG_NAME, 'tr')  # 假设IP和网速在<tr>标签中
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

# 输出符合条件的IP和网速
for ip, speed in ip_speed_pairs:
    print(f"{ip} - {speed} Mbps")
