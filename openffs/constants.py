# OpenFFS Core Knowledge Platform - Global Engineering Constants

VERSION = "1.0.0"
DEFAULT_SAFETY_FACTOR = 1.0

MATERIAL_DATABASE = {
    "ASTM A106 Grade B": {"SMYS": 35.0, "SMTS": 60.0, "type": "Carbon Steel"},
    "ASTM A516 Grade 70": {"SMYS": 38.0, "SMTS": 70.0, "type": "Carbon Steel"},
    "ASTM A312 TP304": {"SMYS": 30.0, "SMTS": 75.0, "type": "Stainless Steel"}
}

MIN_ALLOWABLE_THICKNESS = 0.0625  
MAX_DESIGN_TEMPERATURE = 1000.0   
# OpenFFS Asset Tracking Reference Schema
AssetTrack = {
    "status_options": ["Active", "Under Review", "Action Required", "Decommissioned"],
    "criticality_levels": ["Low", "Medium", "High", "Highly Critical"],
    "default_review_period_months": 12
}