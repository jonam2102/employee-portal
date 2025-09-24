from locust import HttpUser, task, between
import random
import string
from datetime import date
import uuid
from datetime import datetime, timedelta

class FastAPIUser(HttpUser):
    wait_time = between(1, 3)

    roles = ["Engineer", "Senior Engineer", "Manager", "HR", "Intern", "Lead", "Director","Architect"]
    cities = ["BLR", "DEL", "CHN", "HYD", "MUM", "PUN", "GOA", "NYC", "MAN", "OYO"]
    

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


    def on_start(self):
        # Register and login once per user
        self.username = f"user_{uuid.uuid4().hex[:6]}"
        self.password = "test123"
        self.client.post("/register", data={"username": self.username, "password": self.password})
        self.client.post("/login", data={"username": self.username, "password": self.password})

    @task
    def view_portal(self):
        self.client.get("/")

    @task
    def view_dashboard_ui(self):
        self.client.get("/dashboard-ui")

    @task
    def view_hiring_ui(self):
        self.client.get("/hiring-ui")

    @task
    def get_dashboard_data(self):
        self.client.get("/dashboard")

    @task
    def get_hiring_trends(self):
        self.client.get("/hiring-trends")

    @task
    def export_employees_csv(self):
        self.client.get("/all-employees")

    @task
    def list_employees(self):
        self.client.get("/employees?skip=0&limit=5")

    @task
    def create_employee(self):
        emp_id = str(random.randint(1000, 9999))
        names = ["Riya", "Karan", "Zoya", "Dev", "Meera", "Arjun", "Sara", "Nikhil", "Tina", "Vikram","Manoj","Nakul","Suresh"
         "Neha", "Amit", "Priya", "Rohan", "Sneha", "Kabir", "Isha", "Varun", "Anjali", "Yash","Himanshu","Srikrishna"
         "Simran", "Raj", "Pooja", "Aditya", "Naina", "Harsh", "Divya", "Siddharth", "Komal", "Abhay",
         "Tanvi", "Jay", "Lavanya", "Om", "Rekha", "Farhan", "Ira", "Nitin", "Ayesha", "Ravi",
         "Shreya", "Manav", "Bhavna", "Deepak", "Nandini", "Kunal", "Swati", "Akhil", "Trisha", "Gaurav"]
        payload = {
            "id": emp_id,
            "name": random.choice(names),
            "role": "Engineer",
            "date_of_birth": "1990-01-01",
            "date_of_hiring": str(date.today()),
            "address": "123 Main Street"
        }
        self.client.post("/employee", json=payload)

    @task
    def update_employee(self):
        emp_id = str(random.randint(100, 200)) # Replace with a known ID or dynamically track created ones
        payload = {
            "id": emp_id,
            "name": "John Updated",
            "role": "Senior Engineer",
            "date_of_birth": "1990-01-01",
            "date_of_hiring": str(date.today()),
            "address": "456 Updated Street"
        }
        self.client.put(f"/employee/{emp_id}", json=payload)

    @task
    def delete_employee(self):
        emp_id = str(random.randint(101, 200))  # Replace with a known ID or dynamically track created ones
        self.client.delete(f"/employee/{emp_id}")

    @task
    def get_employee_by_id(self):
        emp_id = str(random.randint(100,200))   # Replace with a known ID
        self.client.get(f"/employee/{emp_id}")

    @task
    def get_metrics(self):
        self.client.get("/metrics")

    @task
    def health_check(self):
        self.client.get("/health")
