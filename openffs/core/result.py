"""Assessment result envelope - the engineering deliverable."""


class Suitability:
    SUITABLE = "Suitable"
    SUITABLE_GRIND = "Suitable - Grind Out"
    SUITABLE_PLUG_WELD = "Suitable - Plug Weld"
    SUITABLE_REINFORCE = "Suitable - Reinforce"
    SUITABLE_REDUCED = "Suitable with Reduced MAWP"
    SUITABLE_REDUCED_CAPACITY = "Suitable - Reduced Capacity"
    ESCALATE_L2 = "Not Suitable - Escalate to Level 2"
    ESCALATE_L3 = "Not Suitable - Escalate to Level 3"
    NOT_SUITABLE_IMMEDIATE = "Not Suitable - Immediate Repair/Replacement"
    REPLACE = "Replace"
    REPAIR_AND_RETURN = "Suitable - Repair and Return to Service"
    _SUITABLE_SET = frozenset({SUITABLE, SUITABLE_GRIND, SUITABLE_PLUG_WELD,
        SUITABLE_REINFORCE, SUITABLE_REDUCED, SUITABLE_REDUCED_CAPACITY, REPAIR_AND_RETURN})
    _ESCALATE_SET = frozenset({ESCALATE_L2, ESCALATE_L3})


class AssessmentResult:
    def __init__(self, component_id, track, level, suitability, governing_clause,
                 rsf=None, mawp=None, remaining_life=None, dc_ratio=None,
                 inputs_echo=None, calculation_log=None, warnings=None, metadata=None):
        self.component_id = component_id; self.track = track; self.level = level
        self.suitability = suitability; self.governing_clause = governing_clause
        self.rsf = rsf; self.mawp = mawp; self.remaining_life = remaining_life; self.dc_ratio = dc_ratio
        self.inputs_echo = inputs_echo or {}; self.calculation_log = calculation_log or []
        self.warnings = warnings or []; self.metadata = metadata or {}
    @property
    def is_suitable(self): return self.suitability in Suitability._SUITABLE_SET
    @property
    def requires_escalation(self): return self.suitability in Suitability._ESCALATE_SET
    def to_dict(self):
        return {"component_id": self.component_id, "track": self.track, "level": self.level,
                "suitability": self.suitability, "governing_clause": self.governing_clause,
                "rsf": self.rsf, "mawp": self.mawp, "remaining_life": self.remaining_life,
                "dc_ratio": self.dc_ratio, "inputs_echo": self.inputs_echo,
                "calculation_log": self.calculation_log, "warnings": self.warnings, "metadata": self.metadata}
    def __repr__(self): return f"AssessmentResult({self.component_id}, L{self.level}, {self.suitability!r})"
