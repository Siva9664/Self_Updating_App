from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pathlib import Path
import json
import time
import re
from typing import List, Optional
import math
import random
import uuid
from updater import check_updates, update_modules, get_local_versions

app = FastAPI(
    title="Self-Updating Calculator App",
    description="Secure calculator with auto-update capability",
    version="1.0.1"
)

# Security: CORS - only allow same origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Security: Trusted hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["127.0.0.1", "localhost"]
)

# Rate limiting storage
request_history = {}

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting: max 100 requests per minute per IP"""
    client_ip = request.client.host
    current_time = time.time()
    
    if client_ip not in request_history:
        request_history[client_ip] = []
    
    # Clean old requests (older than 60 seconds)
    request_history[client_ip] = [
        req_time for req_time in request_history[client_ip] 
        if current_time - req_time < 60
    ]
    
    # Check limit
    if len(request_history[client_ip]) >= 100:
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded. Max 100 requests per minute."}
        )
    
    request_history[client_ip].append(current_time)
    response = await call_next(request)
    return response

@app.middleware("http")
async def security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    return response

# Serve static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Load configuration
CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except:
        return {
            "auto_update": {
                "enabled": True,
                "check_interval_minutes": 5,
                "auto_install": True,
                "show_notification": True
            }
        }

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

@app.get("/")
def home():
    return FileResponse("app/templates/calculator.html", media_type="text/html")

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "version": "1.0.1",
        "timestamp": time.time(),
        "services": {
            "calculator": "available",
            "converters": "available",
            "utils": "available"
        }
    }

@app.get("/version")
def get_version():
    """Get current local app version"""
    versions = get_local_versions()
    return {
        "current_version": versions.get("app", "1.0.0"),
        "all_versions": versions
    }

@app.get("/check")
def check():
    return check_updates()

@app.get("/update")
def update():
    return update_modules()

@app.get("/settings")
def get_settings():
    config = load_config()
    return {
        "auto_update": config.get("auto_update", {})
    }

@app.post("/settings")
def update_settings(settings: dict):
    config = load_config()
    if "auto_update" in settings:
        config["auto_update"] = settings["auto_update"]
    save_config(config)
    return {"status": "Settings updated", "settings": config}

# ========== CALCULATION FUNCTIONS ==========

from typing import List, Optional
import math

def validate_number(value, name="value", allow_zero=True):
    """Validate numeric input"""
    if not isinstance(value, (int, float)):
        raise HTTPException(status_code=400, detail=f"{name} must be a number")
    if math.isnan(value) or math.isinf(value):
        raise HTTPException(status_code=400, detail=f"{name} must be a valid number")
    if not allow_zero and value == 0:
        raise HTTPException(status_code=400, detail=f"{name} cannot be zero")
    return value

def validate_expression(expr):
    """Validate mathematical expression for security"""
    if not expr or not isinstance(expr, str):
        return False
    # Only allow safe characters
    allowed_pattern = r'^[\d\+\-\*\/\^\(\)\.\s\_a-zA-Z]+$'
    if not re.match(allowed_pattern, expr):
        return False
    # Block dangerous patterns
    dangerous = ['__', 'import', 'exec', 'eval', 'compile', 'open', 'file', 'os', 'sys', 'subprocess']
    for pattern in dangerous:
        if pattern in expr.lower():
            return False
    return True

@app.get("/calc/add")
def calc_add(a: float, b: float):
    """Add two numbers"""
    try:
        a = validate_number(a, "a")
        b = validate_number(b, "b")
        result = a + b
        if math.isinf(result):
            raise HTTPException(status_code=400, detail="Result is too large")
        return {"operation": "add", "a": a, "b": b, "result": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Calculation error: {str(e)}")

@app.get("/calc/subtract")
def calc_subtract(a: float, b: float):
    """Subtract two numbers"""
    return {"operation": "subtract", "a": a, "b": b, "result": a - b}

@app.get("/calc/multiply")
def calc_multiply(a: float, b: float):
    """Multiply two numbers"""
    return {"operation": "multiply", "a": a, "b": b, "result": a * b}

@app.get("/calc/divide")
def calc_divide(a: float, b: float):
    """Divide two numbers"""
    try:
        a = validate_number(a, "a")
        b = validate_number(b, "b", allow_zero=False)
        result = a / b
        return {"operation": "divide", "a": a, "b": b, "result": round(result, 10)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Calculation error: {str(e)}")

@app.get("/calc/power")
def calc_power(base: float, exponent: float):
    """Calculate power"""
    return {"operation": "power", "base": base, "exponent": exponent, "result": math.pow(base, exponent)}

@app.get("/calc/sqrt")
def calc_sqrt(n: float):
    """Calculate square root"""
    if n < 0:
        return {"error": "Cannot calculate square root of negative number"}
    return {"operation": "sqrt", "n": n, "result": math.sqrt(n)}

@app.get("/calc/factorial")
def calc_factorial(n: int):
    """Calculate factorial"""
    if n < 0:
        return {"error": "Cannot calculate factorial of negative number"}
    if n > 170:
        return {"error": "Number too large"}
    return {"operation": "factorial", "n": n, "result": math.factorial(n)}

@app.get("/calc/percentage")
def calc_percentage(value: float, percent: float):
    """Calculate percentage of a value"""
    result = (value * percent) / 100
    return {"operation": "percentage", "value": value, "percent": percent, "result": result}

@app.post("/calc/expression")
def calc_expression(expression: dict):
    """Evaluate a mathematical expression safely"""
    try:
        expr = expression.get("expression", "")
        
        # Validate expression
        if not validate_expression(expr):
            raise HTTPException(status_code=400, detail="Invalid expression format")
        
        # Length limit
        if len(expr) > 500:
            raise HTTPException(status_code=400, detail="Expression too long (max 500 chars)")
        
        # Safe evaluation - only allow basic math operators and functions
        allowed_names = {
            "abs": abs, "max": max, "min": min,
            "pow": pow, "round": round,
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
            "pi": math.pi, "e": math.e
        }
        
        result = eval(expr, {"__builtins__": {}}, allowed_names)
        
        # Validate result
        if math.isnan(result) or math.isinf(result):
            raise HTTPException(status_code=400, detail="Result is not a valid number")
        
        return {"expression": expr, "result": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid expression: {str(e)}")

# Unit Converters
@app.get("/convert/temperature")
def convert_temperature(value: float, from_unit: str, to_unit: str):
    """Convert temperature between Celsius, Fahrenheit, Kelvin"""
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()
    
    # Convert to Celsius first
    if from_unit == "c":
        celsius = value
    elif from_unit == "f":
        celsius = (value - 32) * 5/9
    elif from_unit == "k":
        celsius = value - 273.15
    else:
        return {"error": f"Unknown unit: {from_unit}. Use c, f, or k"}
    
    # Convert from Celsius to target
    if to_unit == "c":
        result = celsius
    elif to_unit == "f":
        result = (celsius * 9/5) + 32
    elif to_unit == "k":
        result = celsius + 273.15
    else:
        return {"error": f"Unknown unit: {to_unit}. Use c, f, or k"}
    
    return {"value": value, "from": from_unit, "to": to_unit, "result": round(result, 2)}

@app.get("/convert/length")
def convert_length(value: float, from_unit: str, to_unit: str):
    """Convert length between units (m, km, cm, mm, ft, in, mi)"""
    # All conversions to meters
    to_meters = {
        "m": 1, "km": 1000, "cm": 0.01, "mm": 0.001,
        "ft": 0.3048, "in": 0.0254, "mi": 1609.344
    }
    
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()
    
    if from_unit not in to_meters or to_unit not in to_meters:
        return {"error": f"Unknown units. Available: {list(to_meters.keys())}"}
    
    meters = value * to_meters[from_unit]
    result = meters / to_meters[to_unit]
    
    return {"value": value, "from": from_unit, "to": to_unit, "result": round(result, 4)}

@app.get("/convert/weight")
def convert_weight(value: float, from_unit: str, to_unit: str):
    """Convert weight between units (kg, g, lb, oz, ton)"""
    # All conversions to kg
    to_kg = {
        "kg": 1, "g": 0.001, "mg": 0.000001,
        "lb": 0.453592, "oz": 0.0283495, "ton": 1000
    }
    
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()
    
    if from_unit not in to_kg or to_unit not in to_kg:
        return {"error": f"Unknown units. Available: {list(to_kg.keys())}"}
    
    kg = value * to_kg[from_unit]
    result = kg / to_kg[to_unit]
    
    return {"value": value, "from": from_unit, "to": to_unit, "result": round(result, 4)}

# Utility Functions
@app.get("/utils/random")
def utils_random(min: int = 0, max: int = 100):
    """Generate random number"""
    import random
    return {"min": min, "max": max, "result": random.randint(min, max)}

@app.get("/utils/uuid")
def utils_uuid():
    """Generate UUID"""
    import uuid
    return {"uuid": str(uuid.uuid4())}

@app.post("/utils/sum")
def utils_sum(numbers: List[float]):
    """Sum a list of numbers"""
    return {"numbers": numbers, "sum": sum(numbers), "count": len(numbers)}

@app.post("/utils/average")
def utils_average(numbers: List[float]):
    """Calculate average of numbers"""
    if not numbers:
        return {"error": "Empty list"}
    return {"numbers": numbers, "average": sum(numbers) / len(numbers), "count": len(numbers)}
