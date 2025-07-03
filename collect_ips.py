import requests
from bs4 import BeautifulSoup
import re
from ipwhois import IPWhois
import os
import ipaddress

def extract_ips_and_speeds(url, speed_threshold=10):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code != 200:
        print(f"无法访问 {url}，状态码: {response.status_code}")
        return {}

    soup = BeautifulSoup(response.text, "html.parser")
    tbody = soup.find("tbody")
    if not tbody:
        print("页面结构异常，找不到<tbody>标签")
        return {}

    results = {}

    for tr in tbody.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 6:
            continue

        # 提取所有列文本，方便调试
        cols = [td.get_text(strip=True) for td in tds]
        # print(cols)  # 取消注释可调试查看列内容

        ip = cols[2]
        loss = cols[3]
        speed_text = cols[5]

        # 验证IP格式，过滤异常数据
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            # print(f"跳过非法IP: {ip}")
            continue

        # 从速度列提取数字部分，忽略单位
        speed_match = re.match(r"([\d\.]+)", speed_text)
        if not speed_match:
            continue
        speed = float(speed_match.group(1))

        if speed >= speed_threshold:
            results[ip] = {
                "loss": loss,
                "speed": speed,
            }

    return results

def get_country_for_ip(ip, cache):
    if ip in cache:
        return cache[ip]
    try:
        obj = IPWhois(ip)
        res = obj.lookup_rdap(depth=1)
        country = res.get("asn_country_code", "Unknown")
    except Exception as e:
        # print(f"查询 {ip} 国家失败: {e}")
        country = "Unknown"
    cache[ip] = country
    return country

def save_results(results, filename="ip.txt"):
    if os.path.exists(filename):
        os.remove(filename)

    with open(filename, "w", encoding="utf-8") as f:
        for ip, info in sorted(results.items()):
            country = info.get("country", "Unknown")
            f.write(f"{ip}\t丢包率: {info['loss']}\t速度: {info['speed']} mb/s\t国家: {country}\n")

    print(f"已保存 {len(results)} 条符合条件的IP到 {filename}")

def main():
    url = "https://api.uouin.com/cloudflare.html"
    speed_threshold = 10

    print(f"从 {url} 提取速度≥{speed_threshold} mb/s 的IP...")

    results = extract_ips_and_speeds(url, speed_threshold)
    print(f"共提取到 {len(results)} 个符合条件的IP，开始查询国家码...")

    cache = {}
    for ip in results:
        results[ip]["country"] = get_country_for_ip(ip, cache)

    save_results(results)

if __name__ == "__main__":
    main()
