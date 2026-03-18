import urllib.request
import json
from datetime import datetime, timedelta

CITY_COORDS = {
    "mumbai":(19.076,72.877),"delhi":(28.613,77.209),"bangalore":(12.971,77.594),
    "chennai":(13.082,80.270),"hyderabad":(17.385,78.486),"kolkata":(22.572,88.363),
    "ahmedabad":(23.022,72.571),"pune":(18.520,73.856),"jaipur":(26.912,75.787),
    "lucknow":(26.846,80.946),"surat":(21.170,72.831),"bhopal":(23.259,77.412),
    "nagpur":(21.145,79.088),"indore":(22.718,75.857),"patna":(25.594,85.137),
    "vadodara":(22.307,73.181),"coimbatore":(11.016,76.955),"visakhapatnam":(17.686,83.218)
}

def get_coords(location):
    loc = location.strip().lower()
    for city, coords in CITY_COORDS.items():
        if city in loc:
            return coords
    return (20.593, 78.962)

def estimate_irradiance(cloud_cover, temperature):
    max_irr = 1000
    cloud_f = 1 - (cloud_cover/100)*0.75
    temp_f  = 1 - max(0,(temperature-25)*0.004)
    return round(max_irr * cloud_f * temp_f, 1)

def get_weather_forecast(location):
    lat, lon = get_coords(location)
    url = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
           f"&daily=temperature_2m_max,temperature_2m_min,cloudcover_mean,precipitation_sum,windspeed_10m_max"
           f"&current_weather=true&timezone=Asia%2FKolkata&forecast_days=7")
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
        current     = data.get("current_weather", {})
        temperature = current.get("temperature", 30)
        daily       = data.get("daily", {})
        dates       = daily.get("time", [])
        temp_max    = daily.get("temperature_2m_max", [])
        temp_min    = daily.get("temperature_2m_min", [])
        cloud_cover = daily.get("cloudcover_mean", [])
        precipitation = daily.get("precipitation_sum", [])
        windspeed   = daily.get("windspeed_10m_max", [])
        cloud_today = cloud_cover[0] if cloud_cover else 30
        irradiance  = estimate_irradiance(cloud_today, temperature)
        forecast = []
        for i in range(min(7, len(dates))):
            cc  = cloud_cover[i] if i < len(cloud_cover) else 30
            tmp = temp_max[i]    if i < len(temp_max) else temperature
            irr = estimate_irradiance(cc, tmp)
            forecast.append({
                "date": dates[i], "temp_max": round(tmp,1),
                "temp_min": round(temp_min[i] if i<len(temp_min) else tmp-5, 1),
                "cloud_cover": round(cc,1),
                "precipitation": round(precipitation[i] if i<len(precipitation) else 0, 1),
                "windspeed": round(windspeed[i] if i<len(windspeed) else 0, 1),
                "irradiance": irr,
                "solar_score": round((1-cc/100)*10, 1)
            })
        return {"location":location,"latitude":lat,"longitude":lon,"temperature":temperature,
                "cloud_cover":cloud_today,"solar_irradiance":irradiance,"forecast":forecast,"source":"Open-Meteo"}
    except Exception as e:
        temperature = 32.0; cloud_cover_val = 25.0
        irradiance  = estimate_irradiance(cloud_cover_val, temperature)
        today = datetime.now()
        forecast = []
        for i in range(7):
            day = today + timedelta(days=i)
            cc  = 20+(i*5)%40; tmp = 30+(i%3)
            forecast.append({"date":day.strftime("%Y-%m-%d"),"temp_max":tmp,"temp_min":tmp-6,
                "cloud_cover":cc,"precipitation":0,"windspeed":15,"irradiance":estimate_irradiance(cc,tmp),
                "solar_score":round((1-cc/100)*10,1)})
        return {"location":location,"latitude":lat,"longitude":lon,"temperature":temperature,
                "cloud_cover":cloud_cover_val,"solar_irradiance":irradiance,"forecast":forecast,"source":"Offline fallback"}
