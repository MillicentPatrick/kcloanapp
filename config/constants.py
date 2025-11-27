# Kenyan Industry Categories
INDUSTRY_CATEGORIES = [
    "Agriculture - Coffee",
    "Agriculture - Tea", 
    "Agriculture - Horticulture",
    "Agriculture - Dairy",
    "Agriculture - Poultry",
    "Manufacturing - Food Processing",
    "Manufacturing - Textiles",
    "Manufacturing - Construction Materials",
    "Building & Construction - Residential",
    "Building & Construction - Commercial", 
    "Building & Construction - Infrastructure",
    "Services - IT",
    "Services - Hospitality",
    "Services - Healthcare",
    "Services - Education",
    "Trade - Retail",
    "Trade - Wholesale",
    "Trade - Import/Export"
]

# CBK Regulatory Limits
CBK_LIMITS = {
    "single_obligor_limit": 0.25,  # 25% of core capital
    "sector_exposure_limit": 0.30,  # 30% of total portfolio
    "max_debt_service_ratio": 0.50,  # 50%
    "min_liquidity_ratio": 0.20,  # 20%
    "min_capital_adequacy": 0.14  # 14%
}

# Risk Weight Categories
RISK_WEIGHTS = {
    "Agriculture": 0.75,
    "Manufacturing": 0.65,
    "Building & Construction": 0.80,
    "Services": 0.60,
    "Trade": 0.70
}

# Industry Benchmarks for Ratios
INDUSTRY_BENCHMARKS = {
    "current_ratio": {"min": 1.5, "max": 3.0},
    "debt_to_equity": {"min": 0.3, "max": 2.0},
    "debt_service_ratio": {"min": 1.5, "max": float('inf')},
    "roe": {"min": 0.15, "max": float('inf')},
    "roa": {"min": 0.05, "max": float('inf')}
}

# Risk Rating Scales
RISK_RATING_SCALE = {
    'Very Low': 1,
    'Low': 2,
    'Medium': 3,
    'High': 4,
    'Very High': 5
}

# Loan Decision Codes
LOAN_DECISIONS = {
    'APPROVE': 'Approved',
    'APPROVE_CONDITIONAL': 'Approved with Conditions',
    'DECLINE': 'Declined',
    'REFER': 'Referred to Committee'
}

# PDF Report Settings
REPORT_SETTINGS = {
    'bank_name': 'Kenyan Commercial Bank',
    'bank_logo': 'assets/bank_logo.png',
    'footer_text': 'Confidential - For Internal Use Only'
}

# Kenyan Counties (for location data)
KENYAN_COUNTIES = [
    "Mombasa", "Kwale", "Kilifi", "Tana River", "Lamu", "Taita-Taveta", "Garissa",
    "Wajir", "Mandera", "Marsabit", "Isiolo", "Meru", "Tharaka-Nithi", "Embu",
    "Kitui", "Machakos", "Makueni", "Nyandarua", "Nyeri", "Kirinyaga", "Murang'a",
    "Kiambu", "Turkana", "West Pokot", "Samburu", "Trans Nzoia", "Uasin Gishu",
    "Elgeyo-Marakwet", "Nandi", "Baringo", "Laikipia", "Nakuru", "Narok", "Kajiado",
    "Kericho", "Bomet", "Kakamega", "Vihiga", "Bungoma", "Busia", "Siaya",
    "Kisumu", "Homa Bay", "Migori", "Kisii", "Nyamira", "Nairobi"
]