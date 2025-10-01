from fastapi import FastAPI, Request, Form, HTTPException,  Query, Form , Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse,  StreamingResponse
import csv
from io import StringIO
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date, datetime, timezone
from passlib.context import CryptContext
import redis
import json
import os 
from collections import defaultdict
from redis_python.logger import logger
from prometheus_fastapi_instrumentator import Instrumentator


app = FastAPI(title="Employee Info API")
# Redis connection

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
r = redis.Redis.from_url(REDIS_URL, decode_responses=True)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Simulated user database
users_db = {
    "admin": pwd_context.hash("secret123"),
    "manoj": pwd_context.hash("bankingMA"),
    "alice": pwd_context.hash("design@2025")
}

# Pydantic model for employee
class Employee(BaseModel):
        id: str = Field(..., pattern=r"^\d+$", description="Numeric employee ID")
        name: str = Field(..., min_length=2, max_length=50, description="Employee name")
        role: str = Field(..., min_length=2, max_length=30, description="Employee role")
        date_of_birth: date
        date_of_hiring: date
        address: str = Field(..., min_length=5, max_length=100)

        @validator("role")
        def validate_role(cls, v):
            allowed_roles = {"Engineer", "Senior Engineer", "Manager", "HR", "Intern", "Lead", "Director", "Architect"}
            if v not in allowed_roles:
                raise ValueError(f"Role must be one of: {', '.join(allowed_roles)}")
            return v

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url.path} from {request.client.host}")
    response = await call_next(request)
    return response

# 🔐 Login page
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# 🔐 Login handler
@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    logger.info(f"Login attempt for user: {username}")
    hashed = users_db.get(username)
    if not hashed or not pwd_context.verify(password, hashed):
        logger.warning(f"Failed login for user: {username}")
        return RedirectResponse(url="/login?error=1", status_code=302)
    
    logger.info(f"Successful login for user: {username}")
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="auth", value="true", httponly=True)
    response.set_cookie(key="username", value=username)
    return response

# Page for Registration
@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register_user(username: str = Form(...), password: str = Form(...)):
    if username in users_db:
        logger.warning(f"Registration failed: username '{username}' already exists")
        return RedirectResponse(url="/register?error=1", status_code=302)
    users_db[username] = pwd_context.hash(password)
    logger.info(f"New user registered: {username}")
    return RedirectResponse(url="/login", status_code=302)


# 🔒 Protected portal
@app.get("/", response_class=HTMLResponse)
async def employee_portal(request: Request):
    if request.cookies.get("auth") != "true":
        return RedirectResponse(url="/login")
    username = request.cookies.get("username", "Unknown")
    logger.info(f"Portal accessed by: {username}")
    return templates.TemplateResponse("index.html", {"request": request})


# 🔍 Get employee by ID
@app.get("/employee/{emp_id}")
async def get_employee(emp_id: str):
    if not r.exists(emp_id):
        raise HTTPException(status_code=404, detail="Employee not found")
    logger.info(f"Employee fetched: {emp_id}")
    return json.loads(r.get(emp_id))

# ✅ Create employee (no duplicates)
@app.post("/employee", summary="Create a new employee")
async def create_employee(emp: Employee):
   if r.exists(emp.id):
        raise HTTPException(status_code=400, detail=f"Employee with ID {emp.id} already exists")

   for key in r.keys():
        try:
            existing = json.loads(r.get(key))
            if existing["name"] == emp.name and existing["date_of_birth"] == str(emp.date_of_birth):
                raise HTTPException(status_code=400, detail="Duplicate employee detected based on name and date of birth")
        except Exception as e:
            logger.warning(f"Invalid data for key {key}: {e}")
            continue

   r.set(emp.id, emp.json())
   logger.info(f"Employee created: {emp.id}")
   return {"message": "Employee created successfully"}
# ✏️ Update employee
@app.put("/employee/{emp_id}", summary="Update an existing employee")
async def update_employee(emp_id: str, emp: Employee):
    if not r.exists(emp_id):
        raise HTTPException(status_code=404, detail="Employee not found")
    r.set(emp_id, emp.json())
    logger.info(f"Employee updated: {emp_id}")
    return {"message": "Employee updated successfully"}

# 🗑️ Delete employee
@app.delete("/employee/{emp_id}", summary="Delete an employee")
async def delete_employee(emp_id: str):
        if not r.exists(emp_id):
            raise HTTPException(status_code=404, detail="Employee not found")
        r.delete(emp_id)
        logger.info(f"Employee deleted: {emp_id}")
        return {"message": "Employee deleted successfully"}

# 📋 List employees with filters
@app.get("/employees", summary="List employees with filters and pagination")
async def list_employees(
    role: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 10
):
    keys = r.keys()
    employees = []
    for key in keys:
        data = json.loads(r.get(key))
        if role and data["role"] != role:
            continue
        if name and name.lower() not in data["name"].lower():
            continue
        employees.append(data)
    logger.info(f"Employees listed: {len(employees)} found")
    return employees[skip:skip+limit]

#Dashboard Analytics to Show analytics on Employee data
@app.get("/dashboard")

async def analytics_dashboard(request: Request, role: str = ""):
    keys = r.keys()
    if not keys:
        return {
            "total_employees": 0,
            "roles": {},
            "age_stats": {}
        }
    ages = []
    role_counts = {}
    for key in keys:
        emp = json.loads(r.get(key))
        emp_role = emp.get("role", "Unknown")
        dob = emp.get("date_of_birth")
        
        
        # Apply role filter if provided
        if role and emp_role.lower() != role.lower():
            continue

        role_counts[emp_role] = role_counts.get(emp_role, 0) + 1

        try:
            birth_date = datetime.strptime(dob, "%Y-%m-%d")
            today = datetime.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            ages.append(age)
            
        except Exception as e:
            logger.warning(f"Invalid DOB for employee {emp.get('id')}: {dob} — {e}")
            continue


    # Aggregate role counts

    age_stats = {
        "average_age": round(sum(ages) / len(ages), 1) if ages else None,
        "youngest": min(ages) if ages else None,
        "oldest": max(ages) if ages else None
    }
    
    
    logger.info("Dashboard analytics generated")
    return {
        "total_employees": len(keys),
        "roles": role_counts,
        "age_stats": age_stats
    }


# Dashboard UI 

@app.get("/dashboard-ui", response_class=HTMLResponse)
async def dashboard_ui(request: Request):
    if request.cookies.get("auth") != "true":
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("dashboard.html", {"request": request})

# 📤 Export all employees
@app.get("/all-employees")
async def get_all_employees():
    keys = r.keys()
    if not keys:
        raise HTTPException(status_code=404, detail="No employee data found")

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Name", "Role", "Date of Birth", "Address"])

    for key in keys:
        emp = json.loads(r.get(key))
        writer.writerow([
            emp.get("id", ""),
            emp.get("name", ""),
            emp.get("role", ""),
            emp.get("date_of_birth", ""),
            emp.get("address", ""),
            emp.get("date_of_hiring", "")
        ])

    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={
        "Content-Disposition": "attachment; filename=employees.csv"
    })

@app.get("/hiring-trends")
async def hiring_trends():
    keys = r.keys()
    hires_by_month = defaultdict(int)

    for key in keys:
        try:
            emp = json.loads(r.get(key))
            hiring_date = emp.get("date_of_hiring")
            if not hiring_date:
                continue
            dt = datetime.strptime(hiring_date.strip(), "%Y-%m-%d")
            month_key = dt.strftime("%Y-%m")
            hires_by_month[month_key] += 1
        except Exception as e:
            logger.warning(f"Invalid hiring date for {key}: {e}")
            continue

    sorted_months = sorted(hires_by_month.keys())
    trend_data = {
        "months": sorted_months,
        "hires": [hires_by_month[m] for m in sorted_months]
    }

    logger.info(f"Hiring trends generated: {trend_data}")
    return trend_data

@app.get("/hiring-ui", response_class=HTMLResponse)
async def hiring_ui(request: Request):
    if request.cookies.get("auth") != "true":
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("hiring.html", {"request": request})

@app.get("/health", summary="Health check endpoint")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


Instrumentator().instrument(app).expose(app)

