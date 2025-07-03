import requests
from bs4 import BeautifulSoup
from ipwhois import IPWhois
import os
import re

def extract_ips_and_speeds_from_table(url):
    """
    解析网页表格，提取“优选IP”和“速度(mb/s)”
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"无法访问 {url}, 状态码: {response.status_code}")
            return {}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = {}
        
        # 假设IP在表格中“优选IP”列，速度在“速度”列
        # 找表格中的所有行<tr>
        rows = soup.find_all('tr')
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 7:
                continue
            
            ip = cols[2].text.strip()  # 第3列“优选IP”
            speed_str = cols[5].text.strip()  # 第6列“速度”，如“43.85mb/s”
            
            # 验证ip格式
            if not re.match(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', ip):
                continue
            
            # 提取数字部分速度
            match = re.search(r'([\d.]+)', speed_str.lower())
            if match:
                speed = float(match.group(1))
                results[ip] = speed
        
        return results
    except Exception as e:
        print(f"解析网页表格时出错: {e}")
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
    print(f"已保存 {len(ips_with_country_speed)} 个符合条件的 IP 到 {filename}")

def fetch_and_save_ips(urls, min_speed=10):
    all_ips_speeds = {}
    for url in urls:
        print(f"从 {url} 提取IP和速度...")
        ips_speeds = extract_ips_and_speeds_from_table(url)
        all_ips_speeds.update(ips_speeds)
    
    print(f"共提取到 {len(all_ips_speeds)} 个IP，筛选速度≥{min_speed} MB/s，开始查询国家码...")
    cache = {}
    filtered = {}
    for ip, speed in all_ips_speeds.items():
        if speed >= min_speed:
            country = get_country_for_ip(ip, cache)
            filtered[ip] = (country, speed)
            print(f"IP: {ip}, 速度: {speed} MB/s, 国家: {country}")
    
    save_ips_to_file(filtered)

if __name__ == "__main__":
    target_urls = [
        "https://api.uouin.com/cloudflare.html",  # 你网页地址
    ]
    fetch_and_save_ips(target_urls, min_speed=10)
