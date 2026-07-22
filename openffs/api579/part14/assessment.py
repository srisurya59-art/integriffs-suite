"""Part 14 - Structural Integrity main assessment."""
import math
from typing import List, Optional
from openffs.core.result import AssessmentResult, Suitability
from openffs.core.calculation import CalculationLog
from openffs.core.exceptions import ValidationError
from openffs.api579.part14.sections import get_section


MEMBER_BEAM = "beam"; MEMBER_COLUMN = "column"; MEMBER_BRACE = "brace"; MEMBER_PLATE = "plate"
MEMBER_TYPES = {MEMBER_BEAM, MEMBER_COLUMN, MEMBER_BRACE, MEMBER_PLATE}


def uts_from_hardness(hb):
    if hb <= 0: raise ValidationError(f"HB must be > 0")
    return 3.45 * hb


def yield_from_hardness(hb): return 0.7 * uts_from_hardness(hb)


def effective_section_properties(section, gouges_on_flange=None, gouges_on_web=None, perforations=None):
    A_orig = section["A"]; Sx_orig = section["Sx"]; Sy_orig = section.get("Sy", 0.5 * Sx_orig)
    Ix_orig = section["Ix"]; Iy_orig = section.get("Iy", 0.5 * Ix_orig)
    tw = section.get("tw", 0); tf = section.get("tf", 0); bf = section.get("bf", 0); d = section.get("d", 0)
    A_loss = 0.0; flange_loss_frac = 0.0; web_loss_frac = 0.0
    for g in (gouges_on_flange or []):
        vol = g["L_mm"] * g["W_mm"] * g["d_mm"]; A_loss += vol
        if bf * tf > 0: flange_loss_frac += vol / (bf * tf)
    for g in (gouges_on_web or []):
        vol = g["L_mm"] * g["W_mm"] * g["d_mm"]; A_loss += vol
        if d * tw > 0: web_loss_frac += vol / (d * tw)
    for p in (perforations or []):
        vol = p["L_mm"] * p["W_mm"]; A_loss += vol
        if d * tw > 0: web_loss_frac += vol / (d * tw)
        if bf * tf > 0: flange_loss_frac += vol / (bf * tf)
    flange_loss_frac = min(flange_loss_frac, 0.95); web_loss_frac = min(web_loss_frac, 0.95)
    A_eff = max(A_orig - A_loss, 0.05 * A_orig)
    Sx_eff = Sx_orig * (1.0 - 0.6 * flange_loss_frac)
    Sy_eff = Sy_orig * (1.0 - 0.6 * web_loss_frac)
    Ix_eff = Ix_orig * (1.0 - 0.5 * flange_loss_frac)
    Iy_eff = Iy_orig * (1.0 - 0.5 * web_loss_frac)
    return {"A_eff_mm2": A_eff, "Sx_eff_mm3": Sx_eff, "Sy_eff_mm3": Sy_eff,
            "Ix_eff_mm4": Ix_eff, "Iy_eff_mm4": Iy_eff,
            "flange_loss_fraction": flange_loss_frac, "web_loss_fraction": web_loss_frac}


def stress_concentration(aspect_ratio, location="edge"):
    if location == "perforation": return 3.5
    if aspect_ratio >= 5.0: return 2.5
    if aspect_ratio >= 2.0: return 2.5 + 0.5 * (1.0 / aspect_ratio)
    return 3.0


def assess_structural_member(component_id, section_designation, member_type,
                              demand_moment, demand_shear, demand_axial,
                              hardness_hb, gouges=None, perforations=None,
                              level=1, safety_factor_l1=1.5, safety_factor_l2=1.15):
    if member_type not in MEMBER_TYPES: raise ValueError(f"Unknown member_type: {member_type}")
    if level not in (1, 2): raise ValueError(f"Level must be 1 or 2")
    log = CalculationLog()
    section = get_section(section_designation)
    gouges_flange = [g for g in (gouges or []) if g.get("on", "flange") == "flange"]
    gouges_web = [g for g in (gouges or []) if g.get("on", "flange") == "web"]
    eff = effective_section_properties(section, gouges_flange, gouges_web, perforations)
    log.add("E-1", "Effective section properties", {"section": section_designation, "A_eff": eff["A_eff_mm2"], "Sx_eff": eff["Sx_eff_mm3"]}, eff, "-")
    uts = uts_from_hardness(hardness_hb); sy = yield_from_hardness(hardness_hb)
    log.add("E-2", "Material strength from HB", {"HB": hardness_hb, "UTS_est": uts, "Sy_est": sy}, {"UTS_MPa": uts, "Sy_MPa": sy}, "MPa")
    stress_bending = (demand_moment / eff["Sx_eff_mm3"]) if (eff["Sx_eff_mm3"] > 0 and demand_moment != 0) else 0.0
    stress_axial = (demand_axial / eff["A_eff_mm2"]) if (eff["A_eff_mm2"] > 0 and demand_axial != 0) else 0.0
    stress_shear = 0.0
    if demand_shear != 0:
        tw = section.get("tw", 0); d = section.get("d", 0)
        if tw > 0 and d > 0: stress_shear = demand_shear / (d * tw)
    s_combined = math.sqrt(stress_bending ** 2 + 3 * stress_shear ** 2) + abs(stress_axial)
    dc_ratio_l1 = s_combined / sy * safety_factor_l1
    log.add("E-3", "DC ratio (Level 1)", {"stress_bending": stress_bending, "stress_shear": stress_shear, "stress_axial": stress_axial, "Sy_est": sy}, dc_ratio_l1, "-")
    inputs = {"component_id": component_id, "section": section_designation, "member_type": member_type, "HB": hardness_hb,
              "demand_M_Nmm": demand_moment, "demand_V_N": demand_shear, "demand_N_N": demand_axial,
              "gouges": gouges or [], "perforations": perforations or [], "level": level}
    warnings = []
    if level == 1:
        if dc_ratio_l1 <= 1.0: verdict = Suitability.SUITABLE; dc_final = dc_ratio_l1
        elif dc_ratio_l1 <= 1.15:
            verdict = Suitability.SUITABLE_REDUCED_CAPACITY; dc_final = dc_ratio_l1
            warnings.append(f"DC={dc_ratio_l1:.3f} reduced capacity.")
        else:
            verdict = Suitability.ESCALATE_L2; dc_final = dc_ratio_l1
            warnings.append(f"DC={dc_ratio_l1:.3f} escalate.")
    else:
        kt = 1.0
        if perforations: kt = stress_concentration(0.0, location="perforation")
        elif gouges:
            g = max(gouges, key=lambda x: x["L_mm"] * x["W_mm"])
            kt = stress_concentration(g["L_mm"] / max(g["d_mm"], 0.1))
        log.add("E-4", "Stress concentration Kt", {"source": "perforation" if perforations else "gouge"}, kt, "-")
        s_peak = s_combined * kt
        dc_ratio_l2 = s_peak / sy * safety_factor_l2
        log.add("E-5", "Peak DC (Level 2)", {"s_combined": s_combined, "Kt": kt, "s_peak": s_peak, "Sy_est": sy}, dc_ratio_l2, "-")
        if dc_ratio_l2 <= 1.0: verdict = Suitability.SUITABLE_PLUG_WELD if perforations else Suitability.SUITABLE_GRIND
        elif dc_ratio_l2 <= 1.20: verdict = Suitability.SUITABLE_REINFORCE; warnings.append("Reinforce.")
        elif dc_ratio_l2 <= 1.50: verdict = Suitability.SUITABLE_REDUCED_CAPACITY; warnings.append("Reduce capacity.")
        else: verdict = Suitability.REPLACE; warnings.append(f"DC_L2={dc_ratio_l2:.3f} replace.")
        dc_final = dc_ratio_l2
    return AssessmentResult(component_id=component_id, track="structural", level=level,
        suitability=verdict, governing_clause=f"API 579-1/ASME FFS-1 2021, Part 14 ({member_type})",
        dc_ratio=round(dc_final, 4), inputs_echo=inputs, calculation_log=log.to_plain(),
        warnings=warnings, metadata={"A_eff_mm2": eff["A_eff_mm2"], "Sx_eff_mm3": eff["Sx_eff_mm3"],
        "UTS_est_MPa": uts, "Sy_est_MPa": sy, "section_designation": section_designation})
