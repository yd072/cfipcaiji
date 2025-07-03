import requests
import re
import os
from ipwhois import IPWhois

def extract_ips_with_speed_threshold(url, speed_threshold=10):
    """
    从网页文本中提取IP和速度，过滤速度>=speed_threshold的IP
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"无法访问 {url}, 状态码: {response.status_code}")
            return []
        
        ips = []
        lines = response.text.splitlines()
        for line in lines:
            # 过滤空行
            if not line.strip():
                continue
            
            # 按空白字符拆分（空格或tab）
            cols = re.split(r'\s+', line.strip())
            if len(cols) < 6:
                continue
            
            ip_candidate = cols[2]
            speed_str = cols[5].lower()
            
            # 验证IP格式
            if not re.match(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', ip_candidate):
                continue
            
            # 提取速度中的数字
            m = re.search(r'([\d.]+)', speed_str)
            if not m:
                continue
            speed = float(m.group(1))
            
            if speed >= speed_threshold:
                ips.append(ip_candidate)
        
        return ips
    
    except Exception as e:
        print(f"解析网页出错: {e}")
        return []

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

def fetch_and_save_ips_with_speed_filter(urls, speed_threshold=10):
    all_ips = set()
    for url in urls:
        print(f"从 {url} 提取速度≥{speed_threshold} 的IP...")
        ips = extract_ips_with_speed_threshold(url, speed_threshold)
        all_ips.update(ips)
    print(f"共提取 {len(all_ips)} 个符合条件的IP，开始查询国家码...")
    cache = {}
    ips_with_country = {ip: get_country_for_ip(ip, cache) for ip in all_ips}
    save_ips_to_file(ips_with_country)

if __name__ == "__main__":
    target_urls = [
        "https://api.uouin.com/cloudflare.html",
    ]
    fetch_and_save_ips_with_speed_filter(target_urls, speed_threshold=10)
