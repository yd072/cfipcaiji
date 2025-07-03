import ipaddress
import random
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# CF IP段（示例）
cf_cidrs = [
    "103.21.244.0/22",
    "103.22.200.0/22",
    "103.31.4.0/22"
]

def generate_random_ips(cidrs, count=1000):
    all_ips = []
    for cidr in cidrs:
        net = ipaddress.ip_network(cidr)
        all_ips.extend([str(ip) for ip in net.hosts()])
    return random.sample(all_ips, min(count, len(all_ips)))

def ping_via_itdog(ip):
    try:
        url = "https://api.itdog.cn/ping"
        data = {"ip": ip}
        headers = {
            "Content-Type": "application/json",
            "Origin": "https://www.itdog.cn",
            "Referer": "https://www.itdog.cn/ping",
            "User-Agent": "Mozilla/5.0"
        }
        resp = requests.post(url, json=data, headers=headers, timeout=10)
        if resp.status_code == 200 and "data" in resp.json():
            results = resp.json()["data"]
            latencies = []
            for entry in results:
                if "delay" in entry and entry["delay"] and entry["delay"] != "timeout":
                    try:
                        latencies.append(float(entry["delay"]))
                    except ValueError:
                        continue
            if latencies:
                avg_latency = sum(latencies) / len(latencies)
                return ip, round(avg_latency, 2)
        return ip, None
    except Exception as e:
        return ip, None

def main():
    ips = generate_random_ips(cf_cidrs, 1000)
    print(f"Generated {len(ips)} IPs")

    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(ping_via_itdog, ip) for ip in ips]
        for future in as_completed(futures):
            ip, latency = future.result()
            if latency is not None:
                print(f"{ip} => {latency} ms")
                results.append((ip, latency))

    results.sort(key=lambda x: x[1])
    best_15 = results[:15]

    with open("ip.txt", "w") as f:
        for ip, latency in best_15:
            f.write(f"{ip} {latency} ms\n")

    print("Top 15 saved to ip.txt")

if __name__ == "__main__":
    main()
