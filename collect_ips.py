import requests
import re
import os
import csv
import subprocess
import platform
import random
from ipwhois import IPWhois

def extract_ips_from_web(url):
    """
    从指定网页提取所有 IP 地址
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', response.text)
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

def ping_ip(ip):
    """
    使用系统 ping 命令测量延迟（ms），返回平均延迟时间
    """
    param = "-n" if platform.system().lower() == "windows" else "-c"
    try:
        output = subprocess.check_output(["ping", param, "3", ip], universal_newlines=True)
        # 解析延迟
        if platform.system().lower() == "windows":
            # Windows输出中包含 "Average = XXms"
            m = re.search(r"Average = (\d+)ms", output)
            if m:
                return int(m.group(1))
        else:
            # Linux/macOS格式类似: rtt min/avg/max/mdev = 11.123/12.345/13.456/0.789 ms
            m = re.search(r"rtt min/avg/max/mdev = [\d\.]+/([\d\.]+)/[\d\.]+/[\d\.]+ ms", output)
            if m:
                return float(m.group(1))
    except Exception as e:
        print(f"Ping {ip} 失败: {e}")
    return None  # 测量失败返回 None

def measure_speed(ip):
    """
    模拟测速函数，返回 Mbps，真实测速需要额外实现或调用测速服务
    """
    # TODO: 可替换为真实测速
    return round(random.uniform(5, 50), 2)  # 模拟5~50 Mbps的随机速度

def save_ip_info_to_csv(ip_info_list, filename='ip_info.csv'):
    """
    保存 IP 信息列表到 CSV 文件，包含 IP、国家、延迟、速度
    """
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['IP', 'Country', 'Latency_ms', 'Speed_Mbps'])
        for info in ip_info_list:
            writer.writerow([info['ip'], info['country'], info['latency'], info['speed']])
    print(f"IP 信息已保存到 {filename}")

def filter_fast_ips(csv_file='ip_info.csv', output_file='ip.txt', min_speed=10):
    """
    从 csv_file 中筛选速度 >= min_speed 的 IP 保存到 output_file
    """
    filtered_ips = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                speed = float(row['Speed_Mbps'])
                if speed >= min_speed:
                    filtered_ips.append(row['IP'])
            except:
                continue
    # 写入文件
    if os.path.exists(output_file):
        os.remove(output_file)
    with open(output_file, 'w') as f:
        for ip in sorted(filtered_ips):
            f.write(ip + '\n')
    print(f"筛选出速度 >= {min_speed} Mbps 的 {len(filtered_ips)} 个 IP，保存到 {output_file}")

def fetch_and_save_ips_with_info(urls):
    """
    从多个 URL 提取 IP，查询国家，ping 测延迟，测速，保存到 CSV，筛选速度快的到 txt
    """
    all_ips = set()
    cache = {}

    for url in urls:
        print(f"提取 {url} 的 IP...")
        ips = extract_ips_from_web(url)
        all_ips.update(ips)
    
    print(f"共提取到 {len(all_ips)} 个 IP，开始查询国家、测延迟和测速...")

    ip_info_list = []
    for ip in all_ips:
        country = get_country_for_ip(ip, cache)
        latency = ping_ip(ip)
        speed = measure_speed(ip)
        ip_info_list.append({
            'ip': ip,
            'country': country,
            'latency': latency if latency is not None else 'N/A',
            'speed': speed
        })
        print(f"IP: {ip}, Country: {country}, Latency: {latency}, Speed: {speed} Mbps")
    
    save_ip_info_to_csv(ip_info_list)
    filter_fast_ips()

if __name__ == "__main__":
    target_urls = [
        "https://api.uouin.com/cloudflare.html",
    ]
    fetch_and_save_ips_with_info(target_urls)
