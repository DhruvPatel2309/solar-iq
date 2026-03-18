def calculate_roi(location: str, system_size_kw: float, electricity_rate: float, loan_percent: float = 0, loan_years: int = 5) -> dict:
    cost_per_kw = 65000
    total_cost = round(system_size_kw * cost_per_kw, 0)
    subsidy = round(total_cost * 0.30, 0)
    net_cost = total_cost - subsidy

    from ml_models.weather_forecast import get_weather_forecast
    try:
        w = get_weather_forecast(location)
        irr = w["solar_irradiance"] / 1000 * 5.5
    except:
        irr = 5.5

    daily_kwh = system_size_kw * irr * 0.80
    yearly_kwh = round(daily_kwh * 365, 1)
    annual_savings = round(yearly_kwh * electricity_rate, 0)
    payback_years = round(net_cost / annual_savings, 1) if annual_savings > 0 else 99

    savings_25yr = round(annual_savings * 25, 0)
    roi_25yr = round(savings_25yr - net_cost, 0)

    emi = 0
    if loan_percent > 0:
        loan_amt = net_cost * loan_percent / 100
        r = 0.08 / 12
        n = loan_years * 12
        emi = round(loan_amt * r * (1+r)**n / ((1+r)**n - 1), 0)

    yearly_breakdown = []
    cumulative = -net_cost
    for yr in range(1, 26):
        cumulative += annual_savings
        yearly_breakdown.append({"year": yr, "cumulative": round(cumulative, 0), "savings": annual_savings})

    return {
        "system_size_kw": system_size_kw,
        "total_cost": total_cost,
        "subsidy_30pct": subsidy,
        "net_cost": net_cost,
        "yearly_kwh": yearly_kwh,
        "annual_savings": annual_savings,
        "payback_years": payback_years,
        "roi_25yr": roi_25yr,
        "savings_25yr": savings_25yr,
        "emi_per_month": emi,
        "yearly_breakdown": yearly_breakdown,
        "co2_saved_yearly": round(yearly_kwh * 0.82, 1)
    }
