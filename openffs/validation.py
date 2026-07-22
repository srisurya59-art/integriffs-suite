# OpenFFS Input Validation Core
from .constants import MIN_ALLOWABLE_THICKNESS, MAX_DESIGN_TEMPERATURE

def validate_pressure_vessel_inputs(inputs: dict) -> list:
    errors = []
    t = inputs.get("measured_thickness", 0.0)
    D = inputs.get("outside_diameter", 0.0)
    
    if t < MIN_ALLOWABLE_THICKNESS:
        errors.append(f"Thickness ({t} in) is below minimum safe threshold ({MIN_ALLOWABLE_THICKNESS} in).")
    if D <= 0:
        errors.append("Outside diameter must be a positive non-zero value.")
        
    return errors