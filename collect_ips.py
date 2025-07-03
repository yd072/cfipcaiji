import requests
import re
import os
import csv
from ipwhois import IPWhois

def extract_ips_from_web(url):
    """
    从指定网页提取所有 IP 地址
    """
    try:
        # 设置请求头模拟浏览器访问
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        
        # 检查响应状态
        if response.status_code == 200:
            # 使用正则表达式提取 IP 地址
            return re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', response.text), response.elapsed.total_seconds()
        else:
            print(f"无法访问 {url}, 状态码: {response.status_code}")
            return [], 0
    except Exception as e:
        print(f"抓取网页 {url} 时发生错误: {e}")
        return [], 0

def get_country_for_ip(ip, cache):
    """
    查询 IP 的国家简称，使用缓存避免重复查询
    """
    if ip in cache:
        return cache[ip]
    
    try:
        ipwhois = IPWhois(ip)
        result = ipwhois.lookup_rdap()
        country = result.get('asn_country_code', '未知')
        cache[ip] = country
        return country
    except Exception as e:
        print(f"查询 {ip} 的国家代码失败: {e}")
        cache[ip] = '未知'
        return '未知'

def save_ips_to_csv(ips_with_info, filename='ip_info.csv'):
    """
    将提取的 IP 地址、延迟和国家简称保存到 CSV 文件
    """
    # 写入 CSV 文件
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # 写入表头
        writer.writerow(['IP 地址', '国家简称', '延迟 (秒)', '速度 (秒)'])  # 中文表头
        # 写入数据
        for ip, (country, latency) in sorted(ips_with_info.items()):  # 按 IP 排序
            writer.writerow([ip, country, latency, latency])  # 假设速度等于延迟，实际情况可以调整
    
    print(f"提取到 {len(ips_with_info)} 个 IP 地址，已保存到 {filename}")

def fetch_and_save_ips(urls):
    """
    从多个 URL 提取 IP 地址、延迟、速度及其国家简称并保存到文件
    """
    all_ips_info = {}  # 存储 IP 信息，包括国家、延迟
    cache = {}  # 缓存查询结果，避免重复查询

    # 提取所有 IP 地址及其延迟
    for url in urls:
        print(f"正在提取 {url} 的 IP 地址...")
        ips, latency = extract_ips_from_web(url)
        
        # 存储 IP 和相关信息
        for ip in ips:
            country = get_country_for_ip(ip, cache)
            all_ips_info[ip] = (country, latency)
    
    # 保存结果到 CSV 文件
    save_ips_to_csv(all_ips_info)

if __name__ == "__main__":
    # 要提取 IP 的目标 URL 列表
    target_urls = [
        "https://api.uouin.com/cloudflare.html",  # 示例 URL
    ]
    
    # 提取 IP 并保存
    fetch_and_save_ips(target_urls)
