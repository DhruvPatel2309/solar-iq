def calculate_sizing(monthly_units: float, location: str, panel_type: str = "mono") -> dict:
    from ml_models.weather_forecast import get_weather_forecast
    try:
        w = get_weather_forecast(location)
        irr = w["solar_irradiance"] / 1000 * 5.5
    except:
        irr = 5.5

    efficiency_map = {"mono": 0.20, "poly": 0.16, "thin": 0.12}
    eff = efficiency_map.get(panel_type, 0.20)

    daily_units     = monthly_units / 30
    required_kw     = round(daily_units / (irr * 0.80), 2)
    panel_watt      = 400
    num_panels      = int((required_kw * 1000) / panel_watt) + 1
    roof_area_m2    = round(num_panels * 2.0, 1)
    total_cost      = round(required_kw * 65000, 0)
    annual_savings  = round(monthly_units * 12 * 8, 0)
    payback         = round(total_cost * 0.70 / annual_savings, 1) if annual_savings > 0 else 99

    appliance_guide = []
    if monthly_units <= 100:
        appliance_guide = ["2 fans", "6 LED bulbs", "1 small TV", "Phone charging"]
    elif monthly_units <= 300:
        appliance_guide = ["1 AC (8hr/day)", "Refrigerator", "Washing machine", "All lights & fans"]
    elif monthly_units <= 500:
        appliance_guide = ["2 ACs", "All appliances", "Water heater", "Microwave"]
    else:
        appliance_guide = ["Full home/office", "Multiple ACs", "Heavy appliances", "EV charging"]

    return {
        "monthly_units":   monthly_units,
        "daily_units":     round(daily_units, 2),
        "recommended_kw":  required_kw,
        "num_panels":      num_panels,
        "panel_watt":      panel_watt,
        "roof_area_m2":    roof_area_m2,
        "total_cost":      total_cost,
        "annual_savings":  annual_savings,
        "payback_years":   payback,
        "appliance_guide": appliance_guide,
        "panel_type":      panel_type
    }
