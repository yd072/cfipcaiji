import requests
from bs4 import BeautifulSoup
import re
import os

def extract_ips_speed_threshold(url, speed_threshold=10):
    """
    从网页中提取速度>=speed_threshold的IP及对应速度
    """
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    ips = {}

    tbody = soup.find("tbody")
    if not tbody:
        print("未找到<tbody>，网页结构可能变更")
        return ips

    for tr in tbody.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 6:
            continue
        
        ip = tds[2].get_text(strip=True)
        speed_text = tds[5].get_text(strip=True)  # e.g. "43.85mb/s"
        
        match = re.match(r"([\d\.]+)", speed_text)
        if not match:
            continue
        
        speed = float(match.group(1))
        if speed >= speed_threshold:
            print(f"符合条件: IP={ip}, 速度={speed} mb/s")
            ips[ip] = speed
    
    return ips

def save_ips_to_file(ips_with_speed, filename='ip.txt'):
    """
    保存符合条件的IP列表到文件，只写IP，不写速度
    """
    if os.path.exists(filename):
        os.remove(filename)

    with open(filename, 'w') as f:
        for ip in sorted(ips_with_speed.keys()):
            f.write(ip + "\n")
    print(f"共保存 {len(ips_with_speed)} 个IP到文件 {filename}")

if __name__ == "__main__":
    target_url = "https://api.uouin.com/cloudflare.html"
    speed_limit = 10  # mb/s

    print(f"从 {target_url} 提取速度≥{speed_limit} mb/s 的IP...")
    ips = extract_ips_speed_threshold(target_url, speed_limit)
    print(f"共提取到 {len(ips)} 个符合条件的IP")

    save_ips_to_file(ips)
