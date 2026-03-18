def compare_panels(location: str, area: float) -> dict:
    from ml_models.weather_forecast import get_weather_forecast
    try:
        w = get_weather_forecast(location)
        irr = w["solar_irradiance"] / 200
    except:
        irr = 5.5

    panels = [
        {
            "type": "Monocrystalline",
            "efficiency": 20, "cost_per_watt": 45, "lifespan": 30,
            "temp_coefficient": -0.35, "warranty": "25 years",
            "best_for": "Limited roof space, high performance",
            "color": "#FF8C00"
        },
        {
            "type": "Polycrystalline",
            "efficiency": 16, "cost_per_watt": 35, "lifespan": 25,
            "temp_coefficient": -0.40, "warranty": "20 years",
            "best_for": "Budget-friendly, large rooftops",
            "color": "#4A9EFF"
        },
        {
            "type": "Thin-Film (CIGS)",
            "efficiency": 12, "cost_per_watt": 28, "lifespan": 20,
            "temp_coefficient": -0.25, "warranty": "10 years",
            "best_for": "Curved surfaces, low-light areas",
            "color": "#00C896"
        }
    ]

    results = []
    for p in panels:
        daily_kwh   = area * (p["efficiency"] / 100) * irr
        yearly_kwh  = round(daily_kwh * 365, 1)
        system_kw   = round(area * p["efficiency"] / 100, 2)
        total_cost  = round(system_kw * 1000 * p["cost_per_watt"], 0)
        annual_save = round(yearly_kwh * 8, 0)
        payback     = round(total_cost / annual_save, 1) if annual_save > 0 else 99
        results.append({
            **p,
            "daily_kwh":    round(daily_kwh, 2),
            "yearly_kwh":   yearly_kwh,
            "system_kw":    system_kw,
            "total_cost":   total_cost,
            "annual_savings": annual_save,
            "payback_years":  payback,
            "score": round((yearly_kwh / max(1, total_cost / 10000)) * (p["lifespan"] / 25), 2)
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    results[0]["recommended"] = True
    return {"location": location, "area": area, "panels": results}
