from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn, sqlite3, json, os
from datetime import datetime
from ml_models.solar_predictor import predict_solar_output
from ml_models.weather_forecast import get_weather_forecast
from ml_models.chatbot import get_chatbot_response
from ml_models.roi_calculator import calculate_roi
from ml_models.panel_compare import compare_panels
from ml_models.sizing_tool import calculate_sizing
from ml_models.carbon_tracker import calculate_carbon

app = FastAPI(title="SolarIQ")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_db():
    conn = sqlite3.connect("database/solar.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs("database", exist_ok=True)
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS predictions (id INTEGER PRIMARY KEY AUTOINCREMENT, location TEXT, panel_area REAL, panel_efficiency REAL, predicted_kwh REAL, predicted_date TEXT, created_at TEXT);
        CREATE TABLE IF NOT EXISTS chat_history (id INTEGER PRIMARY KEY AUTOINCREMENT, user_message TEXT, bot_response TEXT, created_at TEXT);
        CREATE TABLE IF NOT EXISTS weather_queries (id INTEGER PRIMARY KEY AUTOINCREMENT, location TEXT, temperature REAL, cloud_cover REAL, solar_irradiance REAL, forecast_json TEXT, created_at TEXT);
        CREATE TABLE IF NOT EXISTS roi_calculations (id INTEGER PRIMARY KEY AUTOINCREMENT, location TEXT, system_size_kw REAL, total_cost REAL, annual_savings REAL, payback_years REAL, roi_25yr REAL, created_at TEXT);
        CREATE TABLE IF NOT EXISTS carbon_records (id INTEGER PRIMARY KEY AUTOINCREMENT, yearly_kwh REAL, co2_saved REAL, trees_equivalent REAL, cars_equivalent REAL, created_at TEXT);
        CREATE TABLE IF NOT EXISTS sizing_records (id INTEGER PRIMARY KEY AUTOINCREMENT, monthly_units REAL, location TEXT, recommended_kw REAL, num_panels INTEGER, roof_area REAL, created_at TEXT);
    """)
    conn.commit(); conn.close()

init_db()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    conn = get_db()
    predictions = [dict(r) for r in conn.execute("SELECT * FROM predictions ORDER BY created_at DESC LIMIT 20").fetchall()]
    roi_records  = [dict(r) for r in conn.execute("SELECT * FROM roi_calculations ORDER BY created_at DESC LIMIT 10").fetchall()]
    conn.close()
    return templates.TemplateResponse("dashboard.html", {"request": request, "predictions": predictions, "roi_records": roi_records})

@app.get("/chatbot", response_class=HTMLResponse)
async def chatbot_page(request: Request):
    return templates.TemplateResponse("chatbot.html", {"request": request})

@app.get("/tools", response_class=HTMLResponse)
async def tools_page(request: Request):
    return templates.TemplateResponse("tools.html", {"request": request})

@app.get("/compare", response_class=HTMLResponse)
async def compare_page(request: Request):
    return templates.TemplateResponse("compare.html", {"request": request})

@app.get("/monitor", response_class=HTMLResponse)
async def monitor_page(request: Request):
    return templates.TemplateResponse("monitor.html", {"request": request})

@app.post("/api/predict")
async def predict(location: str=Form(...), panel_area: float=Form(...), panel_efficiency: float=Form(...), target_date: str=Form(...)):
    try:
        r = predict_solar_output(location, panel_area, panel_efficiency, target_date)
        conn = get_db()
        conn.execute("INSERT INTO predictions (location,panel_area,panel_efficiency,predicted_kwh,predicted_date,created_at) VALUES (?,?,?,?,?,?)", (location,panel_area,panel_efficiency,r["predicted_kwh"],target_date,datetime.now().isoformat()))
        conn.commit(); conn.close()
        return JSONResponse(r)
    except Exception as e: raise HTTPException(500, str(e))

@app.post("/api/weather")
async def weather(location: str=Form(...)):
    try:
        r = get_weather_forecast(location)
        conn = get_db()
        conn.execute("INSERT INTO weather_queries (location,temperature,cloud_cover,solar_irradiance,forecast_json,created_at) VALUES (?,?,?,?,?,?)", (location,r["temperature"],r["cloud_cover"],r["solar_irradiance"],json.dumps(r["forecast"]),datetime.now().isoformat()))
        conn.commit(); conn.close()
        return JSONResponse(r)
    except Exception as e: raise HTTPException(500, str(e))

@app.post("/api/chat")
async def chat(message: str=Form(...)):
    try:
        resp = get_chatbot_response(message)
        conn = get_db()
        conn.execute("INSERT INTO chat_history (user_message,bot_response,created_at) VALUES (?,?,?)", (message,resp,datetime.now().isoformat()))
        conn.commit(); conn.close()
        return JSONResponse({"response": resp})
    except Exception as e: raise HTTPException(500, str(e))

@app.post("/api/roi")
async def roi(location: str=Form(...), system_size_kw: float=Form(...), electricity_rate: float=Form(...), loan_percent: float=Form(0), loan_years: int=Form(5)):
    try:
        r = calculate_roi(location, system_size_kw, electricity_rate, loan_percent, loan_years)
        conn = get_db()
        conn.execute("INSERT INTO roi_calculations (location,system_size_kw,total_cost,annual_savings,payback_years,roi_25yr,created_at) VALUES (?,?,?,?,?,?,?)", (location,system_size_kw,r["total_cost"],r["annual_savings"],r["payback_years"],r["roi_25yr"],datetime.now().isoformat()))
        conn.commit(); conn.close()
        return JSONResponse(r)
    except Exception as e: raise HTTPException(500, str(e))

@app.post("/api/compare")
async def compare(location: str=Form(...), area: float=Form(...)):
    try: return JSONResponse(compare_panels(location, area))
    except Exception as e: raise HTTPException(500, str(e))

@app.post("/api/sizing")
async def sizing(monthly_units: float=Form(...), location: str=Form(...), panel_type: str=Form("mono")):
    try:
        r = calculate_sizing(monthly_units, location, panel_type)
        conn = get_db()
        conn.execute("INSERT INTO sizing_records (monthly_units,location,recommended_kw,num_panels,roof_area,created_at) VALUES (?,?,?,?,?,?)", (monthly_units,location,r["recommended_kw"],r["num_panels"],r["roof_area_m2"],datetime.now().isoformat()))
        conn.commit(); conn.close()
        return JSONResponse(r)
    except Exception as e: raise HTTPException(500, str(e))

@app.post("/api/carbon")
async def carbon(yearly_kwh: float=Form(...), current_source: str=Form("grid")):
    try:
        r = calculate_carbon(yearly_kwh, current_source)
        conn = get_db()
        conn.execute("INSERT INTO carbon_records (yearly_kwh,co2_saved,trees_equivalent,cars_equivalent,created_at) VALUES (?,?,?,?,?)", (yearly_kwh,r["co2_saved_kg"],r["trees_equivalent"],r["cars_equivalent"],datetime.now().isoformat()))
        conn.commit(); conn.close()
        return JSONResponse(r)
    except Exception as e: raise HTTPException(500, str(e))

@app.get("/api/stats")
async def stats():
    conn = get_db()
    data = {
        "predictions": conn.execute("SELECT COUNT(*) as c FROM predictions").fetchone()["c"],
        "roi_calculations": conn.execute("SELECT COUNT(*) as c FROM roi_calculations").fetchone()["c"],
        "chat_messages": conn.execute("SELECT COUNT(*) as c FROM chat_history").fetchone()["c"],
        "total_co2_saved": round(conn.execute("SELECT SUM(co2_saved) as s FROM carbon_records").fetchone()["s"] or 0, 1)
    }
    conn.close()
    return JSONResponse(data)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
