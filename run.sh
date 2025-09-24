#!/bin/bash

set -e

echo "🧹 Cleaning up old containers..."
for svc in redis-init fastapi-app prometheus grafana redis_exporter; do
  docker rm -f $svc 2>/dev/null || echo "$svc not running"
done

echo "🧹 Removing old images..."
for img in manoj/redis-init manoj/employee-dashboard manoj/prometheus manoj/grafana-custom oliver006/redis_exporter ; do
  docker rmi -f $img 2>/dev/null || echo "$img not found"
done

# Create Docker network
docker network create mynet || echo "Network already exists"

echo "🔧 Building Redis container..."
docker build -t manoj/redis-init:latest ./redis_image

echo "🔧 Building FastAPI container..."
docker build -t manoj/employee-dashboard:latest .

echo "🔧 Building Prometheus container..."
docker build -t manoj/prometheus:latest ./prometheus

echo "🔧 Building Grafana container..."
docker build -t manoj/grafana-custom:latest ./grafana

echo "🚀 Starting Redis..."
docker run -d \
  --name redis-init \
  --network mynet \
  -p 6379:6379 \
  manoj/redis-init:latest \
  redis-init --requirepass Admin123 --protected-mode no

echo "🚀 Starting RedisExporter..."
docker run -d \
  --name redis-exporter \
  --network mynet \
  -p 9121:9121 \
  oliver006/redis_exporter \
  --redis.addr=redis://redis-init:6379 \
  --redis.password=Admin123

echo "🚀 Starting FastAPI..."
docker run -d \
  --name fastapi-app \
  --network mynet \
  -p 8000:8000 \
  -e REDIS_URL="redis://:Admin123@redis-init:6379/0" \
  manoj/employee-dashboard:latest

echo "🚀 Starting Prometheus..."
docker run -d \
  --name prometheus \
  --network mynet \
  -p 9090:9090 \
  manoj/prometheus:latest 

echo "🚀 Starting Grafana..."
docker run -d \
  --name grafana \
  --network mynet \
  -p 3000:3000 \
  -e GF_SECURITY_ADMIN_USER=admin \
  -e GF_SECURITY_ADMIN_PASSWORD=grafana123 \
  manoj/grafana-custom:latest

echo "✅ All services are up and running!"
