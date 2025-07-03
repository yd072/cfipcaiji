import requests
import re
import os
import csv
from ipwhois import IPWhois

def extract_ip_latency_speed_from_web(url):
    """
    从网页提取 IP、延迟(ms)、速度(Mbps)
    假设网页中格式类似：
    '1.2.3.4 ... 30ms ... 12.5mb/s'
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"无法访问 {url}, 状态码: {response.status_code}")
            return []

        text = response.text

        # 正则匹配IP、延迟（数字+ms）、速度（数字+mb/s）
        pattern = re.compile(
            r'(\b(?:\d{1,3}\.){3}\d{1,3}\b)[^\d]+(\d+\.?\d*)\s*ms[^\d]+(\d+\.?\d*)\s*mb/s',
            re.I
        )
        results = pattern.findall(text)

        return [(ip, float(latency), float(speed)) for ip, latency, speed in results]

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

def save_ip_info_to_csv(ip_info_list, filename='ip_info.csv'):
    """
    保存 IP 信息列表到 CSV 文件，包含 IP、国家、延迟、速度
    """
    with open(filename, 'w', newline='', encoding='utf-8') as f:
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
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                speed = float(row['Speed_Mbps'])
                if speed >= min_speed:
                    filtered_ips.append(row['IP'])
            except Exception:
                continue
    # 写入文件
    if os.path.exists(output_file):
        os.remove(output_file)
    with open(output_file, 'w', encoding='utf-8') as f:
        for ip in sorted(filtered_ips):
            f.write(ip + '\n')
    print(f"筛选出速度 >= {min_speed} Mbps 的 {len(filtered_ips)} 个 IP，保存到 {output_file}")

def fetch_and_save_ips_with_info_from_web(urls):
    all_info = []
    cache = {}

    for url in urls:
        print(f"提取 {url} 的 IP、延迟和速度...")
        infos = extract_ip_latency_speed_from_web(url)
        if not infos:
            print(f"从 {url} 未提取到任何数据")
        all_info.extend(infos)

    if not all_info:
        print("没有提取到任何 IP 信息，程序结束。")
        return

    # 查询国家信息
    unique_ips = {ip for ip, _, _ in all_info}
    for ip in unique_ips:
        if ip not in cache:
            cache[ip] = get_country_for_ip(ip, cache)

    # 合成最终数据列表
    ip_info_list = []
    for ip, latency, speed in all_info:
        country = cache.get(ip, 'Unknown')
        ip_info_list.append({
            'ip': ip,
            'country': country,
            'latency': latency,
            'speed': speed
        })

    save_ip_info_to_csv(ip_info_list)
    filter_fast_ips()

if __name__ == "__main__":
    target_urls = [
        "https://api.uouin.com/cloudflare.html",  # 示例，替换成你的目标网页
    ]
    fetch_and_save_ips_with_info_from_web(target_urls)
