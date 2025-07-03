import os  # 导入 os 模块
import requests
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import tempfile

def extract_ips_and_speed_from_web(url):
    """
    使用 Selenium 从指定网页提取所有 IP 地址及其网速（单位：mb/s），
    只提取网速大于等于 10mb/s 的 IP。
    """
    try:
        # 创建临时目录作为 Chrome 的用户数据目录
        user_data_dir = tempfile.mkdtemp()

        # 设置 Chrome 驱动和无头模式
        options = Options()
        options.headless = True  # 设置无头模式
        options.add_argument(f"--user-data-dir={user_data_dir}")  # 使用临时目录作为用户数据目录

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # 打开目标网页
        driver.get(url)

        # 等待页面加载
        time.sleep(5)  # 你可以根据页面加载的速度调整等待时间
        
        # 获取网页的 HTML 内容
        html_content = driver.page_source
        
        # 关闭浏览器
        driver.quit()

        # 使用正则表达式提取 IP 和网速
        ip_speed_pairs = re.findall(r'<td>(\d+\.\d+\.\d+\.\d+)</td>.*?<td class="asn">(\d+\.\d+)mb/s</td>', html_content)
        
        # 只选择网速大于或等于 10mb/s 的 IP
        fast_ips = {ip for ip, speed in ip_speed_pairs if float(speed) >= 10}
        
        print(f"筛选后的 IP：{fast_ips}")  # 打印筛选后的 IP

        return fast_ips

    except Exception as e:
        print(f"发生错误：{e}")
        return []

def save_ips_to_file(ips_with_country, filename='ip.txt'):
    """
    将提取的 IP 地址保存到文件
    """
    if os.path.exists(filename):  # 确保导入了 os 模块
        os.remove(filename)

    with open(filename, 'w') as file:
        for ip in sorted(ips_with_country):  # 按 IP 排序
            file.write(f"{ip}\n")
    
    print(f"提取到 {len(ips_with_country)} 个 IP 地址，已保存到 {filename}")

def fetch_and_save_ips(urls):
    """
    从多个 URL 提取 IP 地址并保存到文件
    """
    all_ips = set()

    # 提取所有 IP 地址及其网速
    for url in urls:
        print(f"正在提取 {url} 的 IP 地址和网速...")
        fast_ips = extract_ips_and_speed_from_web(url)
        all_ips.update(fast_ips)

    # 保存结果到文件
    save_ips_to_file(all_ips)

if __name__ == "__main__":
    # 要提取 IP 的目标 URL 列表
    target_urls = [
        "https://api.uouin.com/cloudflare.html",  # 示例 URL
    ]
    
    # 提取 IP 并保存
    fetch_and_save_ips(target_urls)
