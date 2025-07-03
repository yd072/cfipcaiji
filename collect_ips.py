import requests
import re
import os
from ipwhois import IPWhois

def extract_ips_by_speed(url, speed_threshold=10):
    """
    从网页提取IP和速度数字，速度≥阈值的IP被提取（忽略单位）
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"无法访问 {url}, 状态码: {response.status_code}")
            return {}
        
        ips_with_speed = {}
        lines = response.text.splitlines()
        for line in lines:
            # 匹配IP + 速度数字（忽略单位，数字可能是整数或浮点）
            match = re.search(r'(\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b).*?([\d.]+)', line)
            if match:
                ip = match.group(1)
                try:
                    speed = float(match.group(2))
                except ValueError:
                    continue
                if speed >= speed_threshold:
                    ips_with_speed[ip] = speed
        return ips_with_speed
    except Exception as e:
        print(f"解析网页时出错: {e}")
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
            f.write(f"{ip}\t{country}\t{speed}\n")
    print(f"已保存 {len(ips_with_country_speed)} 个符合条件的 IP 到 {filename}")

def fetch_and_save_ips(url, speed_threshold=10):
    print(f"从 {url} 提取速度≥{speed_threshold} 的IP（忽略单位）...")
    ips_with_speed = extract_ips_by_speed(url, speed_threshold)
    print(f"提取到 {len(ips_with_speed)} 个 IP。查询国家码...")
    
    cache = {}
    ips_with_country_speed = {}
    for ip, speed in ips_with_speed.items():
        country = get_country_for_ip(ip, cache)
        ips_with_country_speed[ip] = (country, speed)
        print(f"IP: {ip}，速度: {speed}，国家: {country}")
    
    save_ips_to_file(ips_with_country_speed)

if __name__ == "__main__":
    url = "https://api.uouin.com/cloudflare.html"
    fetch_and_save_ips(url, speed_threshold=10)
