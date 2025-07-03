import requests
import re
import pandas as pd

def extract_ip_speed_and_latency_from_web(url):
    """
    从指定网页提取 IP 地址、延迟、速度等信息，假设页面内容是表格格式
    """
    try:
        # 设置请求头模拟浏览器访问
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        
        # 检查响应状态
        if response.status_code == 200:
            # 假设表格中的字段可以通过正则提取
            ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
            latency_pattern = r'(\d+\.\d+)ms'  # 假设延迟格式为 x.xx ms
            speed_pattern = r'(\d+\.\d+)mb/s'  # 假设速度格式为 x.xx mb/s
            # 模拟一个表格数据提取
            ip_list = re.findall(ip_pattern, response.text)
            latency_list = re.findall(latency_pattern, response.text)
            speed_list = re.findall(speed_pattern, response.text)

            # 假设其他信息字段可以提取，如果表格有类似格式
            data = []
            for ip, latency, speed in zip(ip_list, latency_list, speed_list):
                data.append({
                    "IP": ip, 
                    "Latency (ms)": latency,
                    "Speed (MB/s)": speed,
                })
            
            return data
        else:
            print(f"无法访问 {url}, 状态码: {response.status_code}")
            return []
    except Exception as e:
        print(f"抓取网页 {url} 时发生错误: {e}")
        return []

def save_data_to_csv(data, filename='ip_info.csv'):
    """
    将提取的 IP 地址、延迟和速度信息保存到 CSV 文件，并去除重复的 IP 地址
    """
    df = pd.DataFrame(data)

    # 去除重复的 IP 地址
    df = df.drop_duplicates(subset='IP', keep='first')  # 去重，保留第一次出现的 IP
    
    # 保存去重后的数据到 CSV 文件
    df.to_csv(filename, index=False)
    print(f"数据已保存到 {filename}，且 IP 地址已去重")

def filter_ips_by_speed(input_file='ip_info.csv', output_file='ip.txt', speed_threshold=10):
    """
    从 CSV 文件中筛选出速度大于等于 speed_threshold 的 IP 地址并保存到 ip.txt
    """
    try:
        df = pd.read_csv(input_file)
        
        # 转换 Speed (MB/s) 列为浮动数值
        df['Speed (MB/s)'] = pd.to_numeric(df['Speed (MB/s)'], errors='coerce')
        
        # 筛选出速度大于等于 speed_threshold 的 IP
        filtered_df = df[df['Speed (MB/s)'] >= speed_threshold]
        
        # 提取符合条件的 IP 并保存到文件
        with open(output_file, 'w') as f:
            for ip in filtered_df['IP']:
                f.write(f"{ip}\n")
        
        print(f"符合条件的 IP 已保存到 {output_file}")
    except Exception as e:
        print(f"读取 CSV 文件或筛选时出错: {e}")

def fetch_and_process_ips(urls):
    """
    从多个 URL 提取 IP 地址、延迟和速度信息，保存到 CSV，并筛选速度大于等于 10MB/s 的 IP
    """
    all_data = []

    # 提取所有数据
    for url in urls:
        print(f"正在提取 {url} 的数据...")
        data = extract_ip_speed_and_latency_from_web(url)
        all_data.extend(data)

    # 保存数据到 CSV 文件
    if all_data:
        save_data_to_csv(all_data)
        # 筛选并保存符合条件的 IP 地址到 txt 文件
        filter_ips_by_speed()
    else:
        print("没有提取到任何数据，无法保存到 CSV 文件。")

if __name__ == "__main__":
    # 要提取数据的目标 URL 列表
    target_urls = [
        "https://api.uouin.com/cloudflare.html",
        "https://ip.164746.xyz" # 示例 URL
    ]
    
    # 提取数据并处理
    fetch_and_process_ips(target_urls)
