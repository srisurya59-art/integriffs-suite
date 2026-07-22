"""Part 5 Level 1 - Local metal loss from gouges."""
import math
from typing import List, Optional
from openffs.core.units import Length, MM
from openffs.core.quantities import Gouge
from openffs.core.result import AssessmentResult, Suitability
from openffs.core.calculation import CalculationLog
from openffs.core.exceptions import ValidationError, NegativeEffectiveThickness


def folias_factor(L_mm, D_mm, te_mm):
    if te_mm <= 0 or D_mm <= 0: raise NegativeEffectiveThickness(te_mm, "Folias")
    X2 = (L_mm * L_mm) / (D_mm * te_mm)
    if X2 <= 0: return 1.0
    if X2 > 50.0:
        M = 0.032 * X2 + 3.3
    else:
        inside = 1.0 + 0.6275 * X2 - 0.003375 * X2 * X2
        M = math.sqrt(inside) if inside >= 0 else (0.032 * X2 + 3.3)
    return max(M, 1.0)


def assess_gouge_level1(component_id, D, tnom, tloss_avg, fc, P, S, E,
                         L, W, depth, multi_gouges=None):
    log = CalculationLog()
    inputs = {"component_id": component_id, "D_mm": D, "tnom_mm": tnom,
        "tloss_avg_mm": tloss_avg, "fc_mm": fc, "P_MPa": P, "S_MPa": S, "E": E,
        "primary_L_mm": L, "primary_W_mm": W, "primary_d_mm": depth}
    te_local = tnom - depth - fc
    if te_local <= 0: raise NegativeEffectiveThickness(te_local, "Part 5 E-1")
    log.add("E-1", "Effective thickness at gouge", {"tnom": tnom, "depth": depth, "fc": fc}, te_local, "mm")
    M = folias_factor(L, D, te_local)
    log.add("E-2", "Folias factor M", {"L": L, "D": D, "te": te_local}, M, "-")
    denom = S * E - 0.6 * P
    if denom <= 0: raise ValidationError(f"Geometry infeasible")
    t_rd = (P * D / 2.0) / denom / M
    log.add("E-3", "Required thickness (with Folias)", {"P": P, "D": D, "S": S, "E": E, "M": M}, t_rd, "mm")
    tr_local = tnom - fc - depth
    rsf = tr_local / te_local
    log.add("E-4", "RSF at gouge", {"tr": tr_local, "te": te_local}, rsf, "-")
    warnings = []
    if te_local < t_rd: verdict = Suitability.ESCALATE_L2; warnings.append("te < t_rd; escalate.")
    elif rsf > 1.0: verdict = Suitability.SUITABLE_REDUCED; warnings.append("RSF > 1.0; reduce MAWP.")
    else: verdict = Suitability.SUITABLE_GRIND
    mawp = None
    try:
        num = 2.0 * S * E * te_local; den = D + 1.2 * te_local
        mawp = num / den
        log.add("E-5", "MAWP at corroded condition", {"S": S, "E": E, "te": te_local, "D": D}, mawp, "MPa")
    except Exception: pass
    return AssessmentResult(component_id=component_id, track="pressure", level=1,
        suitability=verdict, governing_clause="API 579-1/ASME FFS-1 2021, Part 5 Level 1",
        rsf=round(rsf, 4), mawp=round(mawp, 4) if mawp is not None else None,
        remaining_life=None, inputs_echo=inputs, calculation_log=log.to_plain(),
        warnings=warnings, metadata={"te_local_mm": te_local, "t_rd_mm": t_rd, "M": M})
