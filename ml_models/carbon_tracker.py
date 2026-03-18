def calculate_carbon(yearly_kwh: float, current_source: str = "grid") -> dict:
    emission_factors = {"grid": 0.82, "diesel": 2.68, "coal": 0.95, "gas": 0.45}
    factor = emission_factors.get(current_source, 0.82)

    co2_saved_kg      = round(yearly_kwh * factor, 1)
    co2_saved_tonnes  = round(co2_saved_kg / 1000, 2)
    trees_equivalent  = round(co2_saved_kg / 21.77, 0)
    cars_equivalent   = round(co2_saved_kg / 4600, 2)
    flights_equivalent= round(co2_saved_kg / 255, 1)
    coal_kg_saved     = round(co2_saved_kg / 2.42, 1)

    milestones = []
    if co2_saved_tonnes >= 1:
        milestones.append(f"🌍 Saved {co2_saved_tonnes} tonnes of CO₂")
    if trees_equivalent >= 10:
        milestones.append(f"🌳 Equal to planting {int(trees_equivalent)} trees")
    if cars_equivalent >= 0.5:
        milestones.append(f"🚗 Like taking {cars_equivalent} cars off road for a year")
    if flights_equivalent >= 1:
        milestones.append(f"✈️ Saved {flights_equivalent} flights worth of emissions")

    yearly_breakdown = []
    for yr in range(1, 26):
        yearly_breakdown.append({
            "year": yr,
            "cumulative_co2": round(co2_saved_kg * yr / 1000, 2),
            "cumulative_trees": int(trees_equivalent * yr)
        })

    return {
        "yearly_kwh":         yearly_kwh,
        "current_source":     current_source,
        "co2_saved_kg":       co2_saved_kg,
        "co2_saved_tonnes":   co2_saved_tonnes,
        "trees_equivalent":   int(trees_equivalent),
        "cars_equivalent":    cars_equivalent,
        "flights_equivalent": flights_equivalent,
        "coal_kg_saved":      coal_kg_saved,
        "milestones":         milestones,
        "yearly_breakdown":   yearly_breakdown
    }
