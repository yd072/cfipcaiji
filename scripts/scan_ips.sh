#!/bin/bash

echo "IP,Latency(ms),CdnTraceStatus"

count=0
max=15

mkdir -p output
> output/ip_info.txt

while read ip; do
  if [[ $count -ge $max ]]; then
    break
  fi

  ping_out=$(ping -c 3 -W 1 $ip | grep 'avg' | awk -F '/' '{print $5}')
  if [[ -z "$ping_out" ]]; then
    ping_out="timeout"
  fi

  trace=$(curl -s --connect-timeout 2 --max-time 3 https://$ip/cdn-cgi/trace | grep warp | cut -d= -f2)

  if [[ "$trace" == "off" || "$trace" == "on" ]]; then
    echo "$ip,$ping_out,ok"
    if [[ "$ping_out" != "timeout" && $(echo "$ping_out < 100" | bc) -eq 1 ]]; then
      echo "$ip" >> output/ip_info.txt
      count=$((count+1))
    fi
  else
    echo "$ip,$ping_out,fail"
  fi
done < "$1"
