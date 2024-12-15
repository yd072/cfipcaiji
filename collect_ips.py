from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import re
import time

# 配置 ChromeDriver 路径
driver_path = '/path/to/chromedriver'  # 替换为你的 ChromeDriver 路径

# 初始化浏览器
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 无头模式
options.add_argument('--disable-gpu')
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=options)

# 目标URL列表
urls = ['https://cf.090227.xyz', 'https://ip.164746.xyz','https://stock.hostmonit.com/CloudFlareYes']

# 正则表达式匹配IP地址
ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'

# 保存IP地址到文件
with open('ip.txt', 'w') as file:
    for url in urls:
        try:
            # 加载网页
            driver.get(url)
            time.sleep(5)  # 等待页面加载完成

            # 提取页面内容
            page_source = driver.page_source

            # 使用正则表达式提取IP地址
            ip_matches = re.findall(ip_pattern, page_source)
            for ip in ip_matches:
                file.write(ip + '\n')

        except Exception as e:
            print(f"动态抓取失败 {url}: {e}")

# 关闭浏览器
driver.quit()
print('IP地址已保存到 ip.txt 文件中。')
