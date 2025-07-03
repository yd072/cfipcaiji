import time
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def extract_ips_and_speeds_with_selenium(url):
    """
    使用 Selenium 和 BeautifulSoup 提取 IP 地址及网速，筛选网速大于或等于 10MB/s 的 IP 地址
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 无界面模式
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)

        # 等待页面加载完毕，等待某个元素出现（比如表格的某一行或列）
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'table'))
        )

        # 获取页面源码并用 BeautifulSoup 解析
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        ip_speed_data = []
        rows = soup.find_all('tr')  # 查找所有行

        for row in rows:
            cols = row.find_all('td')
            if len(cols) > 5:  # 确保该行有足够的列数
                ip = cols[2].text.strip()  # 第 3 列是 优选IP
                speed = cols[5].text.strip()  # 第 6 列是 速度
                
                # 打印每一行的信息用于调试
                print(f"正在解析：IP = {ip}, 网速 = {speed}")
                
                # 使用正则匹配网速格式：例如 '19.68mb/s'
                match = re.match(r'(\d+\.\d+)mb/s', speed)
                if match:
                    speed_value = float(match.group(1))
                    if speed_value >= 10:  # 筛选网速大于等于 10MB/s 的 IP
                        ip_speed_data.append((ip, speed_value))
        
        return ip_speed_data
    except Exception as e:
        print(f"抓取网页时发生错误: {e}")
        return []
    finally:
        driver.quit()

def save_ips_to_file(ips_with_speed, filename='ip_speed.txt'):
    """
    将提取的 IP 地址和网速保存到文件
    """
    # 删除已有文件，确保文件干净
    if os.path.exists(filename):
        os.remove(filename)
    
    # 写入文件
    with open(filename, 'w') as file:
        for ip, speed in sorted(ips_with_speed, key=lambda x: x[1], reverse=True):  # 按网速降序排序
            file.write(f"{ip}#{speed}mb/s\n")
    
    print(f"提取到 {len(ips_with_speed)} 个符合条件的 IP 地址，已保存到 {filename}")

def fetch_and_save_ips(url):
    """
    从 URL 提取 IP 地址和网速，筛选网速大于等于 10MB/s 的 IP 地址并保存到文件
    """
    print(f"正在提取 {url} 的 IP 地址和网速...")
    
    # 获取符合条件的 IP 地址和网速
    ips_with_speed = extract_ips_and_speeds_with_selenium(url)
    
    # 保存结果到文件
    save_ips_to_file(ips_with_speed)

if __name__ == "__main__":
    # 要提取 IP 的目标 URL 列表
    target_url = "https://api.uouin.com/cloudflare.html"  # 替换成你的实际 URL
    
    # 提取 IP 并保存
    fetch_and_save_ips(target_url)
