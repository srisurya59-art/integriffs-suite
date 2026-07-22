# OpenFFS Engineering Engine - Folias Factor Calculation
import math

def calculate_folias_factor(length: float, diameter: float, thickness: float, component_type: str = "cylindrical") -> float:
    if thickness <= 0 or diameter <= 0:
        return 1.0
    param_lambda = (1.285 * length) / math.sqrt(diameter * thickness)
    if component_type.lower() == "cylindrical":
        return math.sqrt(1.0 + 0.48 * (param_lambda ** 2))
    return 1.0