from redis_python.main import app
from fastapi.testclient import TestClient


client = TestClient(app)
def test_csv_export():
    response = client.get("/all-employees")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "Content-Disposition" in response.headers
    assert "ID,Name,Role,Date of Birth" in response.text  # Basic header check

def test_dashboard_ui_page():
    response = client.get("/dashboard-ui", cookies={"auth": "true"})
    assert response.status_code == 200
    assert "Dashboard" in response.text or "canvas" in response.text

def test_hiring_ui_page():
    response = client.get("/hiring-ui", cookies={"auth": "true"})
    assert response.status_code == 200
    assert "Hiring Trends" in response.text or "canvas" in response.text

def test_employee_portal_ui():
    response = client.get("/", cookies={"auth": "true"})
    assert response.status_code == 200
    assert "Employee Portal" in response.text or "form" in response.text
