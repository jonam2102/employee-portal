import redis
import json
from datetime import datetime

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def calculate_age(dob_str):
    dob = datetime.strptime(dob_str, "%Y-%m-%d")
    today = datetime.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

# Assuming employees are stored as a Redis hash: key = "employees", field = employee_id, value = JSON string
def process_employees():
      keys = r.keys()
      for key in keys:
        emp = json.loads(r.get(key))
        role = emp.get("role", "Unknown")
        dob = emp.get("date_of_birth")
        if dob: 
             age = calculate_age(dob)
             print(f"Employee ID: {id}, Age: {age}")

process_employees()
