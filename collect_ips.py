import requests
import re
import os
from ipwhois import IPWhois

def extract_ips_from_web(url):
    """
    从指定网页提取所有 IP 地址
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"无法访问 {url}, 状态码: {response.status_code}")
            return []
        ips = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', response.text)
        return ips
    except Exception as e:
        print(f"抓取网页 {url} 出错: {e}")
        return []

def get_country_for_ip(ip, cache):
    """
    查询 IP 的国家简称，使用缓存避免重复查询
    """
    if ip in cache:
        return cache[ip]
    try:
        ipwhois = IPWhois(ip)
        result = ipwhois.lookup_rdap()
        country = result.get('asn_country_code', 'Unknown')
        cache[ip] = country
        return country
    except Exception as e:
        print(f"查询 {ip} 国家代码失败: {e}")
        cache[ip] = 'Unknown'
        return 'Unknown'

def save_ips_to_file(ips_with_country, filename='ip.txt'):
    """
    将 IP 地址和国家简称保存到文件
    """
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, 'w') as f:
        for ip, country in sorted(ips_with_country.items()):
            f.write(f"{ip}\t{country}\n")
    print(f"已保存 {len(ips_with_country)} 个 IP 到 {filename}")

def fetch_and_save_ips(urls):
    """
    从多个 URL 提取 IP 并保存
    """
    all_ips = set()
    for url in urls:
        print(f"提取 {url} 的 IP...")
        ips = extract_ips_from_web(url)
        all_ips.update(ips)
    print(f"共提取到 {len(all_ips)} 个 IP，开始查询国家码...")
    cache = {}
    ips_with_country = {ip: get_country_for_ip(ip, cache) for ip in all_ips}
    save_ips_to_file(ips_with_country)

if __name__ == "__main__":
    target_urls = [
        "https://api.uouin.com/cloudflare.html",
    ]
    fetch_and_save_ips(target_urls)
