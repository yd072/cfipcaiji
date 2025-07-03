import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from ipwhois import IPWhois
import os

def get_page_source_selenium(url):
    options = Options()
    options.binary_location = "/usr/bin/chromium-browser"  # github runner默认路径
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    html = driver.page_source
    driver.quit()
    return html

def extract_ips_and_speeds(html, speed_threshold=10):
    soup = BeautifulSoup(html, "html.parser")
    ips = {}
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 6:
            continue
        ip = tds[2].text.strip()
        speed_text = tds[5].text.strip()  # 第6列，速度，比如 "43.85mb/s"
        match = re.match(r"([\d\.]+)", speed_text)
        if match:
            speed = float(match.group(1))
            # 打印调试信息
            print(f"IP: {ip}, Speed text: {speed_text}, Speed: {speed}")
            if speed >= speed_threshold:
                ips[ip] = speed
    return ips

def get_country_for_ip(ip, cache):
    if ip in cache:
        return cache[ip]
    try:
        obj = IPWhois(ip)
        res = obj.lookup_rdap(depth=1)
        country = res.get("asn_country_code", "Unknown")
        cache[ip] = country
        return country
    except Exception as e:
        print(f"查询 {ip} 国家码失败: {e}")
        cache[ip] = "Unknown"
        return "Unknown"

def save_ips_to_file(ips_with_country, filename="ip.txt"):
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, "w") as f:
        for ip in sorted(ips_with_country.keys()):
            country = ips_with_country[ip]
            f.write(f"{ip}\t{country}\n")
    print(f"已保存 {len(ips_with_country)} 个符合条件的 IP 到 {filename}")

def fetch_and_save_ips(urls, speed_threshold=10):
    cache = {}
    all_ips = {}
    for url in urls:
        print(f"用Selenium打开 {url} 并提取速度≥{speed_threshold} 的IP...")
        html = get_page_source_selenium(url)
        ips = extract_ips_and_speeds(html, speed_threshold)
        all_ips.update(ips)

    print(f"共提取 {len(all_ips)} 个符合条件的IP，开始查询国家码...")
    ips_with_country = {}
    for ip in all_ips.keys():
        country = get_country_for_ip(ip, cache)
        ips_with_country[ip] = country

    save_ips_to_file(ips_with_country)

if __name__ == "__main__":
    target_urls = [
        "https://api.uouin.com/cloudflare.html"
    ]
    fetch_and_save_ips(target_urls, speed_threshold=10)
