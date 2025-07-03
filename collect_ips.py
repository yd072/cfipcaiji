import re
import os
import csv
from ipwhois import IPWhois
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def fetch_page_source_with_selenium(url, wait=5):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)  # 你需先安装chromedriver
    driver.get(url)
    time.sleep(wait)  # 等待页面加载完成
    html = driver.page_source
    driver.quit()
    return html

def extract_ip_latency_speed_from_html(html):
    results = []
    for line in html.splitlines():
        if not line.strip() or line.startswith("#") or "优选IP" in line:
            continue
        # 尝试用制表符或多个空格分割
        parts = re.split(r'\t+|\s{2,}', line.strip())
        if len(parts) < 6:
            continue
        ip = parts[2]
        latency_str = parts[4]
        speed_str = parts[5]
        try:
            latency = float(latency_str.lower().replace("ms", ""))
            speed = float(speed_str.lower().replace("mb/s", ""))
        except Exception:
            continue
        if re.match(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', ip):
            results.append((ip, latency, speed))
    return results

def get_country_for_ip(ip, cache):
    if ip in cache:
        return cache[ip]
    try:
        obj = IPWhois(ip)
        res = obj.lookup_rdap()
        country = res.get('asn_country_code', 'Unknown')
        cache[ip] = country
        return country
    except Exception as e:
        print(f"查询 {ip} 的国家代码失败: {e}")
        cache[ip] = 'Unknown'
        return 'Unknown'

def save_ip_info_to_csv(ip_info_list, filename='ip_info.csv'):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['IP', 'Country', 'Latency_ms', 'Speed_Mbps'])
        for info in ip_info_list:
            writer.writerow([info['ip'], info['country'], info['latency'], info['speed']])
    print(f"IP 信息已保存到 {filename}")

def filter_fast_ips(csv_file='ip_info.csv', output_file='ip.txt', min_speed=10):
    filtered_ips = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                speed = float(row['Speed_Mbps'])
                if speed >= min_speed:
                    filtered_ips.append(row['IP'])
            except Exception:
                continue

    if os.path.exists(output_file):
        os.remove(output_file)
    with open(output_file, 'w', encoding='utf-8') as f:
        for ip in sorted(filtered_ips):
            f.write(ip + '\n')
    print(f"筛选速度 >= {min_speed} Mbps 的 IP 共 {len(filtered_ips)} 个，保存到 {output_file}")

def fetch_and_save_ips_with_info_from_web(urls):
    cache = {}
    all_info = []
    for url in urls:
        print(f"加载网页 {url} 并提取数据...")
        html = fetch_page_source_with_selenium(url)
        infos = extract_ip_latency_speed_from_html(html)
        if not infos:
            print(f"从 {url} 未提取到任何数据")
        all_info.extend(infos)

    if not all_info:
        print("没有提取到任何 IP 信息，程序结束。")
        return

    unique_ips = {ip for ip, _, _ in all_info}
    for ip in unique_ips:
        if ip not in cache:
            cache[ip] = get_country_for_ip(ip, cache)

    ip_info_list = []
    for ip, latency, speed in all_info:
        country = cache.get(ip, 'Unknown')
        ip_info_list.append({
            'ip': ip,
            'country': country,
            'latency': latency,
            'speed': speed
        })

    save_ip_info_to_csv(ip_info_list)
    filter_fast_ips()

if __name__ == "__main__":
    target_urls = [
        "https://api.uouin.com/cloudflare.html",  # 替换为目标网址
    ]
    fetch_and_save_ips_with_info_from_web(target_urls)
