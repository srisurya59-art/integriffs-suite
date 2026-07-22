"""Part 4 Level 1 main assessment entry point."""
from typing import Optional
from openffs.core.result import AssessmentResult, Suitability
from openffs.core.calculation import CalculationLog
from openffs.core.exceptions import NegativeEffectiveThickness, InvalidCorrosionRate
from openffs.api579.part4.geometry.base import (
    cylindrical_required_thickness, spherical_required_thickness,
    conical_required_thickness, formed_head_required_thickness,
    torispherical_head_factor, ellipsoidal_head_factor)


CYLINDRICAL = "cylindrical"; SPHERICAL = "spherical"; CONICAL = "conical"
TORISPHERICAL = "torispherical"; ELLIPSOIDAL = "ellipsoidal"
GEOMETRIES = {CYLINDRICAL, SPHERICAL, CONICAL, TORISPHERICAL, ELLIPSOIDAL}


def compute_effective_thickness(tnom_mm, tloss_mm, fc_mm, CR_mm_per_yr, tnext_yr):
    te = tnom_mm - tloss_mm - fc_mm - (CR_mm_per_yr * tnext_yr)
    if te <= 0: raise NegativeEffectiveThickness(te, "Part 4 E-1")
    return te


def compute_remaining_life(te_mm, trd_mm, CR_mm_per_yr):
    if CR_mm_per_yr <= 0: raise InvalidCorrosionRate(f"CR must be > 0")
    return (te_mm - trd_mm) / CR_mm_per_yr


def compute_mawp_cylindrical(D_mm, S_MPa, E, te_mm):
    num = 2.0 * S_MPa * E * te_mm; den = D_mm + 1.2 * te_mm
    if den <= 0: raise ValueError(f"Invalid MAWP denominator")
    return num / den


def assess_metal_loss(component_id, geometry, D, tnom, tloss, fc,
                       P, S, E, CR=0.0, tnext=0.0,
                       alpha_deg=None, L_head=None, r_knuckle=None, h_head=None,
                       unit_basis="SI"):
    if geometry not in GEOMETRIES: raise ValueError(f"Unknown geometry: {geometry}")
    log = CalculationLog()
    inputs_echo = {"component_id": component_id, "geometry": geometry,
        "D_mm": D, "tnom_mm": tnom, "tloss_mm": tloss, "fc_mm": fc,
        "P_MPa": P, "S_MPa": S, "E": E, "CR_mm_per_yr": CR, "tnext_yr": tnext}
    te = compute_effective_thickness(tnom, tloss, fc, CR, tnext)
    log.add("E-1", "Effective thickness", {"tnom": tnom, "tloss": tloss, "fc": fc, "CR*tnext": CR * tnext}, te, "mm")
    if geometry == CYLINDRICAL:
        t_rd = cylindrical_required_thickness(P, D / 2.0, S, E, M=1.0)
        log.add("E-2a", "Required thickness (cylindrical)", {"P": P, "R": D / 2.0, "S": S, "E": E, "M": 1.0}, t_rd, "mm")
    elif geometry == SPHERICAL:
        t_rd = spherical_required_thickness(P, D / 2.0, S, E)
        log.add("E-2b", "Required thickness (spherical)", {"P": P, "R": D / 2.0, "S": S, "E": E}, t_rd, "mm")
    elif geometry == CONICAL:
        if alpha_deg is None: raise ValueError("alpha_deg required for CONICAL")
        t_rd = conical_required_thickness(P, D, S, E, alpha_deg)
        log.add("E-2c", "Required thickness (conical)", {"P": P, "D": D, "S": S, "E": E, "alpha_deg": alpha_deg}, t_rd, "mm")
    elif geometry == TORISPHERICAL:
        if L_head is None or r_knuckle is None: raise ValueError("L_head and r_knuckle required")
        M = torispherical_head_factor(L_head, r_knuckle, D)
        t_rd = formed_head_required_thickness(P, D, S, E, M)
        log.add("E-2d", "Required thickness (torispherical)", {"P": P, "D": D, "S": S, "E": E, "M": M}, t_rd, "mm")
    elif geometry == ELLIPSOIDAL:
        if h_head is None: raise ValueError("h_head required for ELLIPSOIDAL")
        M = ellipsoidal_head_factor(h_head, D)
        t_rd = formed_head_required_thickness(P, D, S, E, M)
        log.add("E-2d", "Required thickness (ellipsoidal)", {"P": P, "D": D, "S": S, "E": E, "M": M}, t_rd, "mm")
    tr = tnom - tloss; rsf = tr / te
    log.add("E-3", "Level 1 RSF", {"tr": tr, "te": te}, rsf, "-")
    mawp = None
    if geometry == CYLINDRICAL:
        mawp = compute_mawp_cylindrical(D, S, E, te)
        log.add("E-4a", "MAWP (cylindrical)", {"S": S, "E": E, "te": te, "D": D}, mawp, "MPa")
    rl = None
    if CR > 0:
        rl = compute_remaining_life(te, t_rd, CR)
        log.add("E-5", "Remaining life", {"te": te, "t_rd": t_rd, "CR": CR}, rl, "yr")
    warnings = []
    if te < t_rd: verdict = Suitability.ESCALATE_L2; warnings.append(f"te={te:.3f} < t_rd={t_rd:.3f}; escalate.")
    elif rsf > 1.0: verdict = Suitability.SUITABLE_REDUCED; warnings.append(f"RSF={rsf:.3f} > 1.0; MAWP reduced.")
    else: verdict = Suitability.SUITABLE
    if rl is not None and rl < 0: verdict = Suitability.NOT_SUITABLE_IMMEDIATE
    return AssessmentResult(component_id=component_id, track="pressure", level=1,
        suitability=verdict, governing_clause=f"API 579-1/ASME FFS-1 2021, Part 4 ({geometry})",
        rsf=round(rsf, 4), mawp=round(mawp, 4) if mawp is not None else None,
        remaining_life=round(rl, 2) if rl is not None else None,
        inputs_echo=inputs_echo, calculation_log=log.to_plain(),
        warnings=warnings, metadata={"te_mm": te, "t_rd_mm": t_rd, "tr_mm": tr})
