from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import json
from updater import check_updates, update_modules, get_local_versions

app = FastAPI()

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
    return FileResponse("app/templates/index.html", media_type="text/html")

@app.get("/version")
def get_version():
    """Get current local app version"""
    versions = get_local_versions()
    return {
        "current_version": versions.get("module1", "1.0"),
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

@app.get("/calc/add")
def calc_add(a: float, b: float):
    """Add two numbers"""
    return {"operation": "add", "a": a, "b": b, "result": a + b}

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
    if b == 0:
        return {"error": "Cannot divide by zero"}
    return {"operation": "divide", "a": a, "b": b, "result": a / b}

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
        # Safe evaluation - only allow basic math operators and functions
        allowed_names = {
            "abs": abs, "max": max, "min": min, "sum": sum,
            "pow": pow, "round": round, "math": math,
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
            "pi": math.pi, "e": math.e
        }
        result = eval(expr, {"__builtins__": {}}, allowed_names)
        return {"expression": expr, "result": result}
    except Exception as e:
        return {"error": f"Invalid expression: {str(e)}"}

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
