import pytest
from fastapi.testclient import TestClient
from redis_python.main import app
from datetime import datetime, timedelta
import random

client = TestClient(app)

# 🔧 Mock Redis globally
@pytest.fixture(autouse=True)
def mock_redis(mocker):
    mock_redis = mocker.patch("redis_python.main.r")
    mock_redis.exists.return_value = True
    mock_redis.get.return_value = '{"id":"1","name":"Alice","role":"Engineer","date_of_birth":"1990-01-01","address":"Hyderabad","date_of_hiring":"2022-01-01"}'
    mock_redis.keys.return_value = ["1"]
    mock_redis.hgetall.return_value = {
        b"id": b"1", b"name": b"Alice", b"role": b"Engineer", b"date_of_birth": b"1990-01-01", b"address": b"Hyderabad", b"date_of_hiring": b"2022-01-01"
    }

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_get_employee():
    response = client.get("/employee/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Alice"

def test_dashboard():
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "total_employees" in response.json()

def test_all_employees_csv():
    response = client.get("/all-employees")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "Alice" in response.text

def test_hiring_trends():
    response = client.get("/hiring-trends")
    assert response.status_code == 200
    assert "months" in response.json()

def test_register_page_loads():
    response = client.post("/register", data={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    assert "Employee Portal" in response.text or "form" in response.text

def test_login_page_loads():
    response = client.post("/login", data={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    assert "Employee Portal" in response.text or "form" in response.text

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


