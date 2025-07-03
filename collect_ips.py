import re
import os
from ipwhois import IPWhois
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_page_source_selenium(url):
    options = Options()
    options.add_argument('--headless')  # 无头模式，不打开浏览器窗口
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    html = driver.page_source
    driver.quit()
    return html

def extract_ips_with_speed_threshold_from_html(html, speed_threshold=10):
    ips = []
    lines = html.splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # 按空白分割
        cols = re.split(r'\s+', line)
        if len(cols) < 6:
            continue
        ip_candidate = cols[2]
        speed_str = cols[5].lower()
        if not re.match(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', ip_candidate):
            continue
        m = re.search(r'([\d.]+)', speed_str)
        if not m:
            continue
        speed = float(m.group(1))
        if speed >= speed_threshold:
            ips.append(ip_candidate)
    return ips

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
        print(f"查询IP {ip} 国家失败: {e}")
        cache[ip] = 'Unknown'
        return 'Unknown'

def save_ips_to_file(ips_with_country, filename='ip.txt'):
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, 'w') as f:
        for ip, country in sorted(ips_with_country.items()):
            f.write(f"{ip}\t{country}\n")
    print(f"已保存 {len(ips_with_country)} 个IP到 {filename}")

def fetch_and_save_ips(urls, speed_threshold=10):
    all_ips = set()
    for url in urls:
        print(f"用Selenium打开 {url} 并提取速度≥{speed_threshold} 的IP...")
        html = get_page_source_selenium(url)
        ips = extract_ips_with_speed_threshold_from_html(html, speed_threshold)
        all_ips.update(ips)
    print(f"共提取 {len(all_ips)} 个符合条件的IP，开始查询国家码...")
    cache = {}
    ips_with_country = {ip: get_country_for_ip(ip, cache) for ip in all_ips}
    save_ips_to_file(ips_with_country)

if __name__ == "__main__":
    target_urls = [
        "https://api.uouin.com/cloudflare.html",
    ]
    fetch_and_save_ips(target_urls, speed_threshold=10)
