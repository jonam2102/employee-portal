import redis

def is_redis_running(host='localhost', port=6379):
    try:
        client = redis.StrictRedis(host=host, port=port, db=0)
        response = client.ping()
        return response  # True if Redis is running
    except redis.ConnectionError:
        return False

# Example usage
if is_redis_running():
    print("Redis is running locally.")
else:
    print("Redis is NOT running locally.")
