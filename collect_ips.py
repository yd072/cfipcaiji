import requests
from bs4 import BeautifulSoup
import re
from ipwhois import IPWhois
import os

def fetch_html(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.text

def extract_ips_and_speeds(html, speed_threshold=10):
    soup = BeautifulSoup(html, "html.parser")
    ips = {}
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 6:
            continue
        ip = tds[2].get_text(strip=True)
        speed_text = tds[5].get_text(strip=True)  # 速度列
        match = re.match(r"([\d\.]+)", speed_text)
        if not match:
            continue
        speed = float(match.group(1))
        # print(f"IP: {ip}, Speed: {speed}")
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
        print(f"查询 {ip} 国家失败: {e}")
        cache[ip] = "Unknown"
        return "Unknown"

def save_ips_to_file(ips_with_country, filename="ip.txt"):
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, "w") as f:
        for ip in sorted(ips_with_country.keys()):
            f.write(f"{ip}\t{ips_with_country[ip]}\n")
    print(f"已保存 {len(ips_with_country)} 个符合条件的 IP 到 {filename}")

def fetch_and_save_ips(urls, speed_threshold=10):
    cache = {}
    all_ips = {}
    for url in urls:
        print(f"从 {url} 请求网页并解析速度≥{speed_threshold} 的IP...")
        html = fetch_html(url)
        ips = extract_ips_and_speeds(html, speed_threshold)
        all_ips.update(ips)

    print(f"共提取 {len(all_ips)} 个符合条件的IP，开始查询国家码...")
    ips_with_country = {}
    for ip in all_ips:
        country = get_country_for_ip(ip, cache)
        ips_with_country[ip] = country

    save_ips_to_file(ips_with_country)

if __name__ == "__main__":
    target_urls = [
        "https://api.uouin.com/cloudflare.html"
    ]
    fetch_and_save_ips(target_urls, speed_threshold=10)
