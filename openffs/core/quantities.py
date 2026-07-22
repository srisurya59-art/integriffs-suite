"""Damage representations and composite quantities."""
from typing import Sequence, Optional
from openffs.core.units import Length, CorrosionRate
from openffs.core.exceptions import ValidationError


class DamageType:
    UNIFORM = "uniform"; GOUGE = "gouge"; PIT = "pit"; PERFORATION = "perforation"


class UniformMetalLoss:
    __slots__ = ("tnom", "tloss", "cr")
    def __init__(self, tnom, tloss, cr=None):
        if tloss.value > tnom.value: raise ValidationError(f"tloss ({tloss.value}) cannot exceed tnom ({tnom.value})")
        self.tnom = tnom; self.tloss = tloss; self.cr = cr


class Gouge:
    __slots__ = ("length", "width", "depth", "location")
    def __init__(self, length, width, depth, location=""):
        if depth.value <= 0: raise ValidationError(f"Gouge depth must be positive")
        self.length = length; self.width = width; self.depth = depth; self.location = location
    def __repr__(self):
        return f"Gouge(L={self.length.value}, W={self.width.value}, d={self.depth.value} {self.length.unit})"


class Perforation:
    __slots__ = ("length", "width", "location")
    def __init__(self, length, width, location=""):
        if length.value <= 0 or width.value <= 0: raise ValidationError("Perforation dimensions must be positive")
        self.length = length; self.width = width; self.location = location


class LocalMetalLoss:
    __slots__ = ("member_type", "gouges", "perforations")
    def __init__(self, member_type="structural", gouges=(), perforations=()):
        self.member_type = member_type; self.gouges = tuple(gouges); self.perforations = tuple(perforations)
    @property
    def is_empty(self): return len(self.gouges) == 0 and len(self.perforations) == 0
    @property
    def max_depth(self):
        if not self.gouges and not self.perforations: return None
        if self.perforations: return float("inf")
        return max(g.depth.value for g in self.gouges)
    def __repr__(self):
        return f"LocalMetalLoss(type={self.member_type}, gouges={len(self.gouges)}, perfs={len(self.perforations)})"
