import requests
import re
import os
from ipwhois import IPWhois

def extract_ips_and_speeds_from_web(url):
    """
    从指定网页提取所有 IP 地址及其网速，筛选出网速大于或等于 10MB/s 的 IP 地址
    """
    try:
        # 设置请求头模拟浏览器访问
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        
        # 检查响应状态
        if response.status_code == 200:
            # 使用正则表达式提取每行的 IP 地址和网速
            ip_speed_data = []
            lines = response.text.splitlines()
            for line in lines:
                # 正则匹配 IP 地址和网速信息
                match = re.search(r'(\d+\.\d+\.\d+\.\d+)\s+\d+\.\d+ms\s+(\d+\.\d+)mb/s', line)
                if match:
                    ip = match.group(1)  # IP 地址
                    speed = float(match.group(2))  # 网速，转换为数字
                    if speed >= 10:  # 筛选网速大于等于 10MB/s 的 IP
                        ip_speed_data.append((ip, speed))
            return ip_speed_data
        else:
            print(f"无法访问 {url}, 状态码: {response.status_code}")
            return []
    except Exception as e:
        print(f"抓取网页 {url} 时发生错误: {e}")
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
        print(f"查询 {ip} 的国家代码失败: {e}")
        cache[ip] = 'Unknown'
        return 'Unknown'

def save_ips_to_file(ips_with_country, filename='ip.txt'):
    """
    将提取的 IP 地址和国家简称保存到文件
    """
    # 删除已有文件，确保文件干净
    if os.path.exists(filename):
        os.remove(filename)
    
    # 写入文件
    with open(filename, 'w') as file:
        for ip, country in sorted(ips_with_country.items()):  # 按 IP 排序
            file.write(f"{ip}#{country}\n")    
    
    print(f"提取到 {len(ips_with_country)} 个 IP 地址，已保存到 {filename}")

def fetch_and_save_ips(urls):
    """
    从多个 URL 提取 IP 地址及其国家简称并保存到文件
    """
    all_ips = set()
    cache = {}  # 缓存查询结果，避免重复查询

    # 提取所有 IP 地址和网速
    for url in urls:
        print(f"正在提取 {url} 的 IP 地址和网速...")
        ips_and_speeds = extract_ips_and_speeds_from_web(url)
        for ip, speed in ips_and_speeds:
            all_ips.add(ip)
    
    # 查询国家信息
    print("正在查询 IP 的国家简称...")
    ips_with_country = {ip: get_country_for_ip(ip, cache) for ip in all_ips}

    # 保存结果到文件
    save_ips_to_file(ips_with_country)

if __name__ == "__main__":
    # 要提取 IP 的目标 URL 列表
    target_urls = [
        "https://api.uouin.com/cloudflare.html",  # 示例 URL
    ]
    
    # 提取 IP 并保存
    fetch_and_save_ips(target_urls)
