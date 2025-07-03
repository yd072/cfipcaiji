from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

def setup_driver():
    """
    设置并启动 Chrome WebDriver
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式
    chrome_options.add_argument("--disable-gpu")  # 禁用 GPU，加速加载

    # 下载和启动 WebDriver（GitHub Actions 中使用预安装的 ChromeDriver）
    driver = webdriver.Chrome(options=chrome_options)
    
    return driver

def extract_ip_data_from_web(url):
    """
    从网页中提取 IP 地址、延迟和速度
    """
    driver = setup_driver()
    
    try:
        # 访问网页
        driver.get(url)

        # 等待页面中包含 IP 地址元素加载完成
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//tr/td[1]'))  # 依据 IP 的位置来调整 XPath
        )

        # 提取表格中的 IP 地址、延迟和速度信息
        ip_elements = driver.find_elements(By.XPATH, '//tr/td[1]')  # 假设 IP 在第一列
        latency_elements = driver.find_elements(By.XPATH, '//tr/td[2]')  # 假设延迟在第二列
        speed_elements = driver.find_elements(By.XPATH, '//tr/td[3]')  # 假设速度在第三列

        # 获取文本内容
        ips = [ip.text for ip in ip_elements]
        latencies = [latency.text for latency in latency_elements]
        speeds = [speed.text for speed in speed_elements]

        # 返回整理好的数据
        data = []
        for ip, latency, speed in zip(ips, latencies, speeds):
            data.append({
                "IP": ip,
                "Latency (ms)": latency,
                "Speed (MB/s)": speed
            })

        return data

    except Exception as e:
        print(f"发生错误: {e}")
        return []
    
    finally:
        driver.quit()

def save_data_to_csv(data, filename='ip_info.csv'):
    """
    将提取的 IP 地址、延迟和速度信息保存到 CSV 文件
    """
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"数据已保存到 {filename}")

def filter_ips_by_speed(input_file='ip_info.csv', output_file='ip.txt', speed_threshold=10):
    """
    从 CSV 文件中筛选出速度大于等于 speed_threshold 的 IP 地址并保存到 ip.txt
    """
    try:
        df = pd.read_csv(input_file)
        
        # 转换 Speed (MB/s) 列为浮动数值
        df['Speed (MB/s)'] = pd.to_numeric(df['Speed (MB/s)'], errors='coerce')
        
        # 筛选出速度大于等于 speed_threshold 的 IP
        filtered_df = df[df['Speed (MB/s)'] >= speed_threshold]
        
        # 提取符合条件的 IP 并保存到文件
        with open(output_file, 'w') as f:
            for ip in filtered_df['IP']:
                f.write(f"{ip}\n")
        
        print(f"符合条件的 IP 已保存到 {output_file}")
    except Exception as e:
        print(f"读取 CSV 文件或筛选时出错: {e}")

def fetch_and_process_ips(urls):
    """
    从多个 URL 提取 IP 地址、延迟和速度信息，保存到 CSV，并筛选速度大于等于 10MB/s 的 IP
    """
    all_data = []

    # 提取所有数据
    for url in urls:
        print(f"正在提取 {url} 的数据...")
        data = extract_ip_data_from_web(url)
        all_data.extend(data)

    # 保存数据到 CSV 文件
    if all_data:
        save_data_to_csv(all_data)
        # 筛选并保存符合条件的 IP 地址到 txt 文件
        filter_ips_by_speed()
    else:
        print("没有提取到任何数据，无法保存到 CSV 文件。")

if __name__ == "__main__":
    # 要提取数据的目标 URL 列表
    target_urls = [
        "https://api.uouin.com/cloudflare.html",  # 示例 URL
    ]
    
    # 提取数据并处理
    fetch_and_process_ips(target_urls)
