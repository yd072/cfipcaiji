import requests
import re
import os
from ipwhois import IPWhois

def extract_ips_and_speeds(url):
    """
    从网页文本提取 IP 和速度（mb/s），筛选速度≥10
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"无法访问 {url}, 状态码: {response.status_code}")
            return {}
        
        text = response.text
        
        # 正则解析：序号 电信 IP 丢包 延迟 速度 单位 带宽 查询 时间
        # 重点抓IP和速度，速度数字部分
        pattern = re.compile(
            r'\d+\s+\S+\s+(\b(?:\d{1,3}\.){3}\d{1,3}\b)\s+\S+\s+\S+\s+([\d.]+)mb/s',
            re.IGNORECASE
        )
        
        results = {}
        for ip, speed_str in pattern.findall(text):
            speed = float(speed_str)
            if speed >= 10:
                results[ip] = speed
        return results

    except Exception as e:
        print(f"提取IP和速度失败: {e}")
        return {}

def get_country_for_ip(ip, cache):
    if ip in cache:
        return cache[ip]
    try:
        ipwhois = IPWhois(ip)
        result = ipwhois.lookup_rdap()
        country = result.get('asn_country_code', 'Unknown')
        cache[ip] = country
        return country
    except Exception as e:
        print(f"查询 {ip} 国家码失败: {e}")
        cache[ip] = 'Unknown'
        return 'Unknown'

def save_ips_to_file(ips_with_country_speed, filename='ip.txt'):
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, 'w') as f:
        for ip, (country, speed) in sorted(ips_with_country_speed.items()):
            f.write(f"{ip}\t{country}\t{speed:.2f} MB/s\n")
    print(f"已保存 {len(ips_with_country_speed)} 个符合条件的IP到 {filename}")

def fetch_and_save_ips(urls):
    all_ips_speeds = {}
    for url in urls:
        print(f"从 {url} 提取IP和速度...")
        ips_speeds = extract_ips_and_speeds(url)
        all_ips_speeds.update(ips_speeds)
    
    print(f"共提取到 {len(all_ips_speeds)} 个符合条件的IP，开始查询国家码...")
    cache = {}
    filtered = {}
    for ip, speed in all_ips_speeds.items():
        country = get_country_for_ip(ip, cache)
        filtered[ip] = (country, speed)
        print(f"IP: {ip}, 速度: {speed} MB/s, 国家: {country}")
    
    save_ips_to_file(filtered)

if __name__ == "__main__":
    target_urls = [
        "https://api.uouin.com/cloudflare.html",
    ]
    fetch_and_save_ips(target_urls)
