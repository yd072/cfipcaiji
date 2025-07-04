#!/bin/bash

echo "IP,Latency(ms),CdnTraceStatus"

while read ip; do
  ping_out=$(ping -c 3 -W 1 $ip | grep 'avg' | awk -F '/' '{print $5}')
  if [[ -z "$ping_out" ]]; then
    ping_out="timeout"
  fi

  trace=$(curl -s --connect-timeout 2 --max-time 3 https://$ip/cdn-cgi/trace | grep warp | cut -d= -f2)

  if [[ "$trace" == "off" || "$trace" == "on" ]]; then
    echo "$ip,$ping_out,ok"
  else
    echo "$ip,$ping_out,fail"
  fi
done < "$1"
