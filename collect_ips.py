import time
import requests
import re
from ipwhois import IPWhois

def extract_ips_and_speeds_from_web(url):
    """
    从指定网页提取所有满足条件的 IP 地址及网速
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # 匹配 IP 地址及网速信息
            pattern = r'(\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b)[^\d]*(\d+)\s*(Mbps?|Mb/s)'
            matches = re.findall(pattern, response.text)
            filtered_ips = []
            
            for match in matches:
                ip, speed, unit = match
                speed = int(speed)
                
                if speed >= 10:  # 网速大于或等于 10 Mbps
                    filtered_ips.append(ip)
            
            return filtered_ips
        else:
            print(f"无法访问 {url}, 状态码: {response.status_code}")
            return []
    except Exception as e:
        print(f"抓取网页 {url} 时发生错误: {e}")
        return []

def fetch_and_save_ips(urls):
    """
    从多个 URL 提取 IP 地址及其国家简称并保存到文件
    """
    all_ips = set()
    cache = {}  # 缓存查询结果，避免重复查询

    # 提取所有符合条件的 IP 地址
    for url in urls:
        print(f"正在提取 {url} 的 IP 地址...")
        ips = extract_ips_and_speeds_from_web(url)
        if ips:
            all_ips.update(ips)
        else:
            print(f"未能从 {url} 提取到有效的 IP 地址，稍后重试...")

        # 等待 10 分钟再进行下一次抓取
        print("等待 10 分钟...")
        time.sleep(10 * 60)  # 等待 10 分钟
    
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
