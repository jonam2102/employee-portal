import redis
import time
# Wait for Redis to start
time.sleep(2)

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

try:
    r.ping()
    print("✅ Connected to Redis")

    # Seed data
    r.set("app:status", "initialized")
    r.hset("employee:101", mapping={"name": "Alice", "role": "Engineer"})
    r.hset("employee:102", mapping={"name": "Bob", "role": "Manager"})
    print("🚀 Seeded initial data")

except redis.ConnectionError:
    print("❌ Failed to connect to Redis")
