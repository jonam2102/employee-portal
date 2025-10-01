from fastapi import FastAPI
from fastapi.responses import JSONResponse
import redis
import json

# Create FastAPI app
app = FastAPI(title="Redis Viewer")

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

@app.get("/all-employees", summary="Get all employee entries from Redis")
async def get_all_employees():
    keys = r.keys()
    if not keys:
        return JSONResponse(content={"message": "No entries found"}, status_code=200)

    employees = []
    for key in keys:
        value = r.get(key)
        try:
            parsed = json.loads(value)
            employees.append(parsed)
        except json.JSONDecodeError:
            employees.append({"id": key, "raw_value": value})

    return employees
