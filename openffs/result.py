# OpenFFS Standardized Engineering Result Object
# Objective: Explicit structured calculation outputs for transparency.

class AssessmentResult:
    def __init__(self, level: str, is_acceptable: bool, remaining_life: float = None):
        self.level = level
        self.is_acceptable = is_acceptable
        self.remaining_life = remaining_life
        self.notes = []
