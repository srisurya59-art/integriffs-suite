"""Base helper for Part 4 geometry calculations."""
import math
from openffs.core.exceptions import InvalidGeometry, ValidationError


def cylindrical_required_thickness(P, R, S, E, M=1.0):
    if P <= 0 or R <= 0 or S <= 0: raise InvalidGeometry("Cylindrical t_rd: P/R/S must be > 0")
    if not (0 < E <= 1.0): raise ValidationError(f"Joint efficiency E={E} must be in (0, 1]")
    denom = S * E - 0.6 * P
    if denom <= 0: raise ValidationError(f"Cylindrical geometry infeasible")
    return (P * R) / denom / M


def spherical_required_thickness(P, R, S, E):
    if P <= 0 or R <= 0 or S <= 0: raise InvalidGeometry("Spherical t_rd: invalid P/R/S")
    if not (0 < E <= 1.0): raise ValidationError(f"E={E} must be in (0, 1]")
    denom = 2.0 * S * E - 0.2 * P
    if denom <= 0: raise ValidationError("Spherical geometry infeasible")
    return (P * R) / denom


def conical_required_thickness(P, D, S, E, alpha_deg):
    if P <= 0 or D <= 0 or S <= 0: raise InvalidGeometry("Cone t_rd: invalid P/D/S")
    if not (0 < E <= 1.0): raise ValidationError(f"E={E} must be in (0, 1]")
    cos_a = math.cos(math.radians(alpha_deg))
    if cos_a <= 0: raise InvalidGeometry("Cosine of cone angle <= 0")
    denom = 2.0 * cos_a * S * E - 0.6 * P
    if denom <= 0: raise ValidationError("Cone geometry infeasible")
    return (P * D) / denom


def formed_head_required_thickness(P, D, S, E, M):
    if P <= 0 or D <= 0 or S <= 0: raise InvalidGeometry("Head t_rd: invalid P/D/S")
    if not (0 < E <= 1.0): raise ValidationError(f"E={E} must be in (0, 1]")
    if M <= 0: raise ValidationError(f"Head factor M={M} must be > 0")
    denom = 2.0 * S * E - 0.2 * P
    if denom <= 0: raise ValidationError("Head geometry infeasible")
    return (P * D * M) / denom


def torispherical_head_factor(L, r, D):
    if L <= 0 or r <= 0 or D <= 0: raise InvalidGeometry("Head factor inputs must be > 0")
    M = 0.25 * (3.0 + math.sqrt(L / r)) if r > 0 else 1.0
    return max(M, 1.0)


def ellipsoidal_head_factor(h, D):
    if h <= 0 or D <= 0: raise InvalidGeometry("Ellip head factor: h/D must be > 0")
    if h == 0.5 * D: return 1.0
    M = 0.25 * (3.0 + math.sqrt(max(2.0 * D / (2.0 * h), 0.0)))
    return max(M, 1.0)
