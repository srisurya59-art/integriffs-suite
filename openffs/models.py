# OpenFFS Data Models Module
# Objective: Explicit, readable data containers for engineering components.

class PressureVesselComponent:
    def __init__(self, tag: str, material: str, outside_diameter: float, nominal_thickness: float):
        self.tag = tag
        self.material = material
        self.outside_diameter = outside_diameter
        self.nominal_thickness = nominal_thickness
        self.assessments = []

    def add_assessment(self, assessment_log: dict):
        self.assessments.append(assessment_log)

# OpenFFS Assessment Schema Tracking Metadata
AssessmentMetadata = {
    "supported_levels": ["Level 1 - Screening", "Level 2 - Refined"],
    "code_references": ["API 579-1/ASME FFS-1 Part 4", "ASME Section VIII Div 1/2"],
    "platform_type": "Trusted Knowledge Base Engine"
}

# OpenFFS Material Properties Container Class
class MaterialProperties:
    def __init__(self, spec: str, smys: float, smts: float, allow_stress: float = None):
        self.specification = spec
        self.allowable_stress = allow_stress if allow_stress else (smts / 3.5)

# OpenFFS Vessel Geometry Properties Container
class VesselGeometry:
    def __init__(self, outside_diameter: float, nominal_thickness: float, corrosion_allowance: float = 0.0):
        self.outside_diameter = outside_diameter
        self.nominal_thickness = nominal_thickness
        self.corrosion_allowance = corrosion_allowance

# OpenFFS Operating Conditions Container Class
class OperatingConditions:
    def __init__(self, pressure: float, temperature: float, efficiency: float = 1.0):
        self.internal_pressure = pressure
        self.design_temperature = temperature
        self.joint_efficiency = efficiency

# OpenFFS Damage State Representation Container
class DamageState:
    def __init__(self, flaw_length: float, measured_thickness: float, assessment_level: str = "Level 1"):
        self.flaw_length = flaw_length
        self.measured_thickness = measured_thickness
        self.assessment_level = assessment_level
