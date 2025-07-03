import re
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def extract_ip_speed_and_latency_from_web(url):
    """
    使用 selenium 加载网页并提取 IP、延迟、速度等数据（等待 JS 加载完成）
    """
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 无头模式
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        driver.get(url)

        # 等待页面中包含表格或类似内容加载完毕（你可根据页面内容调整等待条件）
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        time.sleep(2)  # 保守等待额外加载

        page_source = driver.page_source
        driver.quit()

        # 正则提取
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        latency_pattern = r'(\d+\.\d+)ms'
        speed_pattern = r'(\d+\.\d+)mb/s'

        ip_list = re.findall(ip_pattern, page_source)
        latency_list = re.findall(latency_pattern, page_source)
        speed_list = re.findall(speed_pattern, page_source)

        # 构造数据
        data = []
        for ip, latency, speed in zip(ip_list, latency_list, speed_list):
            data.append({
                "IP": ip,
                "Latency (ms)": latency,
                "Speed (MB/s)": speed,
            })

        return data
    except Exception as e:
        print(f"抓取网页 {url} 时出错: {e}")
        return []


def save_data_to_csv(data, filename='ip_info.csv'):
    """
    将提取的数据保存到 CSV，并去重
    """
    df = pd.DataFrame(data)
    df.drop_duplicates(subset='IP', inplace=True)  # 根据 IP 去重
    df.to_csv(filename, index=False)
    print(f"已保存去重后的数据到 {filename}")


def filter_ips_by_speed(input_file='ip_info.csv', output_file='ip.txt', speed_threshold=10):
    """
    筛选速度 ≥ 指定阈值的 IP，并保存到 txt 文件
    """
    try:
        df = pd.read_csv(input_file)
        df['Speed (MB/s)'] = pd.to_numeric(df['Speed (MB/s)'], errors='coerce')
        filtered_df = df[df['Speed (MB/s)'] >= speed_threshold]
        
        with open(output_file, 'w') as f:
            for ip in filtered_df['IP']:
                f.write(f"{ip}\n")
        
        print(f"已保存符合条件的 IP 到 {output_file}")
    except Exception as e:
        print(f"筛选 IP 时出错: {e}")


def fetch_and_process_ips(urls):
    """
    从多个网页提取并处理 IP 数据
    """
    all_data = []
    for url in urls:
        print(f"正在提取：{url}")
        data = extract_ip_speed_and_latency_from_web(url)
        all_data.extend(data)

    if all_data:
        save_data_to_csv(all_data)
        filter_ips_by_speed()
    else:
        print("未提取到数据，CSV 未创建。")


if __name__ == "__main__":
    target_urls = [
        "https://api.uouin.com/cloudflare.html"
    ]
    fetch_and_process_ips(target_urls)
