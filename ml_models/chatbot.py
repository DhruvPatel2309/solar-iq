import re

KNOWLEDGE_BASE = [
    {"keywords":["solar panel","how work","work","function","photovoltaic"],"response":"☀️ **How Solar Panels Work:**\nSolar panels use photovoltaic (PV) cells made of silicon. When sunlight hits these cells, it knocks electrons loose, creating DC electricity. An inverter converts DC to AC for home use.\n\n**Key components:** PV cells → Inverter → Your home → Grid (if excess)"},
    {"keywords":["cost","price","expensive","cheap","affordable","rupee","inr","money"],"response":"💰 **Solar Panel Costs in India (2024):**\n• 1 kW system: ₹60,000 – ₹75,000\n• 3 kW system: ₹1.5 – ₹2.0 Lakhs\n• 5 kW system: ₹2.5 – ₹3.5 Lakhs\n• 10 kW system: ₹5 – ₹7 Lakhs\n\nPayback period: 4–6 years. Government subsidies reduce cost by 20–40%!"},
    {"keywords":["subsidy","government","scheme","pm surya","kusum","benefit"],"response":"🏛️ **Government Solar Subsidies in India:**\n• **PM Surya Ghar Yojana**: Up to ₹78,000 subsidy for rooftop solar\n• **PM-KUSUM**: Solar pumps for farmers\n• **MNRE Rooftop Solar**: 20–40% capital subsidy\n• **Net Metering**: Sell excess power back to grid!\n\nApply at: pmsuryaghar.gov.in"},
    {"keywords":["efficiency","best panel","monocrystalline","polycrystalline","thin film"],"response":"⚡ **Solar Panel Types & Efficiency:**\n• **Monocrystalline**: 18–22% efficiency — Best performance\n• **Polycrystalline**: 15–17% efficiency — Good value\n• **Thin-Film**: 10–13% efficiency — Flexible applications\n\nFor India's high heat: Monocrystalline with good temperature coefficient is best."},
    {"keywords":["battery","storage","backup","night","cloudy"],"response":"🔋 **Solar Battery Storage:**\n• **Lithium-ion (LiFePO4)**: Best — 10+ year life\n• **Lead-acid**: Budget option — 3–5 year life\n\nCost: ₹8,000–₹15,000 per kWh for lithium.\nA 5 kW system typically needs 10 kWh battery storage."},
    {"keywords":["maintenance","clean","maintain","care","service"],"response":"🔧 **Solar Panel Maintenance:**\n• Clean panels every 2–4 weeks (dust reduces output 25%)\n• Use soft cloth and water — no harsh chemicals\n• Annual professional inspection\n• Lifetime: 25–30 years with proper care"},
    {"keywords":["how much","generate","produce","output","kwh","unit","calculate"],"response":"📊 **Solar Energy Output:**\nFormula: **kWh = Area (m²) × Efficiency × Irradiance (kWh/m²/day)**\n\nIndia average: 5–6.5 kWh/m²/day\n\nExample: 20 m², 18% efficiency, 5.5 irradiance:\n= 20 × 0.18 × 5.5 = **19.8 kWh/day**\n\n👉 Use our **Solar Predictor** tool for accurate estimates!"},
    {"keywords":["installation","install","roof","rooftop","setup","space"],"response":"🏠 **Solar Installation Guide:**\n• 1 kW requires ~10 m² of roof space\n• Ideal angle: 10–30° (match your latitude)\n• Face panels **South** in India for max output\n• Installation takes 1–3 days\n• Get 3 quotes from MNRE-certified vendors"},
    {"keywords":["roi","return","payback","savings","profit"],"response":"📈 **Solar ROI & Savings:**\n• Payback period: 4–6 years\n• 25-year savings: ₹5–20 Lakhs\n• Bill reduction: 80–100%\n• Property value increase: 3–4%\n\nWith ₹8/unit and 5 kW system → saves ~₹40,000/year!"},
    {"keywords":["environment","carbon","co2","green","climate","emission"],"response":"🌱 **Environmental Impact:**\n• 1 kW solar saves ~1.5 tonnes CO₂ per year\n• Equal to planting 70 trees annually\n• India solar capacity: 90+ GW (2024) — world's 4th largest!"},
    {"keywords":["net metering","grid","export","sell"],"response":"⚡ **Net Metering in India:**\nNet metering lets you sell excess solar power back to the grid!\n• Your meter runs backwards when exporting power\n• Get credits on your electricity bill\n• Available in all major states\n• Requires approval from your DISCOM"},
    {"keywords":["hello","hi","hey","namaste","greet"],"response":"👋 **Namaste! Welcome to SolarIQ!**\n\nI can help you with:\n• How solar panels work\n• Costs & government subsidies\n• Energy output calculations\n• Installation tips\n• ROI and savings\n• Battery storage\n• Net metering\n\nWhat would you like to know? ☀️"},
]

DEFAULT_RESPONSE = "🤔 I'm not sure about that. Try asking about:\n• **Solar costs** — 'How much does a 5kW system cost?'\n• **Subsidies** — 'What government subsidies are available?'\n• **Output** — 'How much energy can I generate?'\n• **Installation** — 'How to install solar panels?'\n• **ROI** — 'What is the payback period?'"

def get_chatbot_response(message: str) -> str:
    msg   = re.sub(r'[^\w\s]', ' ', message.lower().strip())
    words = set(msg.split())
    best_match, best_score = None, 0
    for entry in KNOWLEDGE_BASE:
        score = 0
        for keyword in entry["keywords"]:
            kw_words = set(keyword.lower().split())
            if kw_words.issubset(words):
                score += len(kw_words) * 2
            elif any(k in msg for k in keyword.lower().split()):
                score += 1
        if score > best_score:
            best_score = score
            best_match = entry
    return best_match["response"] if best_match and best_score > 0 else DEFAULT_RESPONSE
