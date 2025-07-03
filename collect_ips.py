import requests
import re
import os
from ipwhois import IPWhois

def extract_ips_and_speed_from_web(url):
    """
    从指定网页提取所有 IP 地址及其网速（单位：mb/s）
    假设网页中 IP 地址和网速信息格式为 "IP 地址 - 网速 mb/s"
    """
    try:
        # 设置请求头模拟浏览器访问
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        
        # 检查响应状态
        if response.status_code == 200:
            # 打印网页内容的前 2000 个字符，帮助调试
            print("网页内容预览：")
            print(response.text[:2000])  # 只打印前2000个字符，确保足够内容
            
            # 假设网页中 IP 和网速信息格式为 "IP 地址 - 网速 mb/s"
            ip_speed_pairs = re.findall(r'(\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b)\s*-\s*(\d+(\.\d+)?)\s*mb/s', response.text)
            
            print(f"提取到的 IP 和网速对：{ip_speed_pairs}")  # 打印提取出来的数据
            return ip_speed_pairs
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

    # 提取所有 IP 地址及其网速
    for url in urls:
        print(f"正在提取 {url} 的 IP 地址和网速...")
        ip_speed_pairs = extract_ips_and_speed_from_web(url)
        
        # 打印所有提取出的 IP 和网速对，检查数据
        for ip, speed in ip_speed_pairs:
            print(f"IP: {ip}, 网速: {speed} mb/s")  # 打印每个提取出的 IP 和网速
        
        # 只选择网速大于或等于 10mb/s 的 IP
        fast_ips = {ip for ip, speed in ip_speed_pairs if float(speed) >= 10}  # 直接用 10mb/s
        
        print(f"筛选后的 IP：{fast_ips}")  # 打印筛选后的 IP
        
        all_ips.update(fast_ips)
    
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
