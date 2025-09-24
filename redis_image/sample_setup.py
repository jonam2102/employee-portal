import redis, json
import json
import random
from datetime import datetime, timedelta

r = redis.Redis(host='localhost',password="Admin123", port=6379, db=0)


roles = ["Engineer", "Senior Engineer", "Manager", "HR", "Intern", "Lead", "Director","Architect"]
cities = ["BLR", "DEL", "CHN", "HYD", "MUM", "PUN", "GOA", "NYC", "MAN", "OYO"]
names = ["Riya", "Karan", "Zoya", "Dev", "Meera", "Arjun", "Sara", "Nikhil", "Tina", "Vikram","Manoj","Nakul","Suresh"
         "Neha", "Amit", "Priya", "Rohan", "Sneha", "Kabir", "Isha", "Varun", "Anjali", "Yash","Himanshu","Srikrishna"
         "Simran", "Raj", "Pooja", "Aditya", "Naina", "Harsh", "Divya", "Siddharth", "Komal", "Abhay",
         "Tanvi", "Jay", "Lavanya", "Om", "Rekha", "Farhan", "Ira", "Nitin", "Ayesha", "Ravi",
         "Shreya", "Manav", "Bhavna", "Deepak", "Nandini", "Kunal", "Swati", "Akhil", "Trisha", "Gaurav"]

def random_dob(min_age=18, max_age=60):
    today = datetime.today()
    age = random.randint(min_age, max_age)
    birth_date = today - timedelta(days=age*365 + random.randint(0, 364))
    return birth_date.strftime("%Y-%m-%d")

def random_exp(min_exp=1, max_exp=25):
    today = datetime.today()
    exp = random.randint(min_exp,max_exp)
    date_of_hiring = today - timedelta(days=exp*365 + random.randint(0,364))
    return date_of_hiring.strftime("%Y-%m-%d")

for i in range(101, 200):
    record = {
        "id": str(i),
        "name": random.choice(names),
        "role": random.choice(roles),
        "date_of_birth": random_dob(),
        "date_of_hiring": random_exp(),
        "address": random.choice(cities)
    }
    r.set(str(i), json.dumps(record))

print("✅ 100 records inserted successfully.")