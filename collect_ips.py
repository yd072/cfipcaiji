import requests
from bs4 import BeautifulSoup
import re
import os
from ipwhois import IPWhois

def extract_ips_with_speed(url, speed_threshold=10):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"无法访问 {url}, 状态码: {response.status_code}")
            return {}

        soup = BeautifulSoup(response.text, "html.parser")
        tbody = soup.find("tbody")
        if not tbody:
            print("网页中找不到 tbody 标签")
            return {}

        results = {}

        for tr in tbody.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) < 6:
                continue
            
            ip = tds[2].get_text(strip=True)
            loss = tds[3].get_text(strip=True)
            speed_text = tds[5].get_text(strip=True)  # 速度如 "43.85mb/s"

            match = re.match(r"([\d\.]+)", speed_text)
            if not match:
                continue
            speed = float(match.group(1))

            if speed >= speed_threshold:
                print(f"IP: {ip}, 丢包率: {loss}, 速度: {speed} mb/s")
                results[ip] = {"loss": loss, "speed": speed}

        return results

    except Exception as e:
        print(f"提取IP和速度时出错: {e}")
        return {}

def get_country_for_ip(ip, cache):
    if ip in cache:
        return cache[ip]
    try:
        obj = IPWhois(ip)
        res = obj.lookup_rdap(depth=1)
        country = res.get('asn_country_code', 'Unknown')
        cache[ip] = country
        return country
    except Exception as e:
        print(f"查询 {ip} 国家失败: {e}")
        cache[ip] = 'Unknown'
        return 'Unknown'

def save_ips_to_file(ips_with_country, filename='ip.txt'):
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, 'w') as f:
        for ip, info in sorted(ips_with_country.items()):
            f.write(f"{ip}  丢包率: {info['loss']}  速度: {info['speed']} mb/s  国家: {info['country']}\n")
    print(f"已保存 {len(ips_with_country)} 个 IP 到 {filename}")

def fetch_and_save_ips(url, speed_threshold=10):
    print(f"从 {url} 提取速度≥{speed_threshold} mb/s 的IP...")
    ips_info = extract_ips_with_speed(url, speed_threshold)
    if not ips_info:
        print("未提取到符合条件的IP")
        return

    print("开始查询国家码...")
    cache = {}
    for ip in ips_info.keys():
        ips_info[ip]['country'] = get_country_for_ip(ip, cache)

    save_ips_to_file(ips_info)

if __name__ == "__main__":
    target_url = "https://api.uouin.com/cloudflare.html"
    fetch_and_save_ips(target_url, speed_threshold=10)
