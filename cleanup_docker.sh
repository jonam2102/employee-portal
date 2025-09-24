#!/bin/bash

set -e

echo "Stop all Containers ..."

for svc in redis-init fastapi-app prometheus grafana redis-exporter; do
  docker stop -f $svc 2>/dev/null || echo "$svc not running"
done


echo "🧹 Cleaning up old containers..."
for svc in redis-init fastapi-app prometheus grafana redis-exporter; do
  docker rm -f $svc 2>/dev/null || echo "$svc not running"
done

echo "🧹 Removing old images..."
for img in manoj/redis-init manoj/employee-dashboard manoj/prometheus manoj/grafana-custom oliver006/redis_exporter ; do
  docker rmi -f $img 2>/dev/null || echo "$img not found"
done