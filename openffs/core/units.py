"""Typed engineering units. SI primary; Imperial in reporting layer."""
from openffs.core.exceptions import UnitMismatchError

MM = "mm"
IN = "in"
MPA = "MPa"
PSI = "psi"
YEAR = "yr"
MM_PER_YR = "mm/yr"
IN_PER_YR = "in/yr"
CELSIUS = "C"
FAHRENHEIT = "F"
HB = "HB"


class Length:
    __slots__ = ("_value", "_unit")
    def __init__(self, value, unit=MM):
        if not isinstance(value, (int, float)):
            raise TypeError("Length value must be numeric")
        if unit not in (MM, IN):
            raise UnitMismatchError(f"Length unit must be mm or in, got {unit}")
        self._value = float(value); self._unit = unit
    @property
    def value(self): return self._value
    @property
    def unit(self): return self._unit
    def to(self, other_unit):
        if other_unit not in (MM, IN): raise UnitMismatchError(f"Cannot convert to {other_unit}")
        if self._unit == other_unit: return self._value
        if self._unit == MM and other_unit == IN: return self._value / 25.4
        if self._unit == IN and other_unit == MM: return self._value * 25.4
        raise ValueError("Unhandled length conversion")
    def __repr__(self): return f"Length({self._value}, {self._unit!r})"
    def __float__(self): return self._value


class Pressure:
    __slots__ = ("_value", "_unit")
    def __init__(self, value, unit=MPA):
        if not isinstance(value, (int, float)): raise TypeError("Pressure value must be numeric")
        if unit not in (MPA, PSI): raise UnitMismatchError(f"Pressure unit must be MPa or psi")
        self._value = float(value); self._unit = unit
    @property
    def value(self): return self._value
    @property
    def unit(self): return self._unit
    def to(self, other_unit):
        if other_unit not in (MPA, PSI): raise UnitMismatchError("Cannot convert pressure")
        if self._unit == other_unit: return self._value
        if self._unit == MPA and other_unit == PSI: return self._value * 145.038
        if self._unit == PSI and other_unit == MPA: return self._value / 145.038
        raise ValueError("Unhandled pressure conversion")
    def __repr__(self): return f"Pressure({self._value}, {self._unit!r})"


class Time:
    __slots__ = ("_value",)
    def __init__(self, value, unit=YEAR): self._value = float(value)
    @property
    def value(self): return self._value
    @property
    def unit(self): return YEAR
    def __repr__(self): return f"Time({self._value}, yr)"


class CorrosionRate:
    __slots__ = ("_value", "_unit")
    def __init__(self, value, unit=MM_PER_YR):
        if not isinstance(value, (int, float)): raise TypeError("CorrosionRate value must be numeric")
        if unit not in (MM_PER_YR, IN_PER_YR): raise UnitMismatchError(f"CorrosionRate unit must be mm/yr or in/yr")
        self._value = float(value); self._unit = unit
    @property
    def value(self): return self._value
    @property
    def unit(self): return self._unit
    def to(self, other_unit):
        if other_unit not in (MM_PER_YR, IN_PER_YR): raise UnitMismatchError("Cannot convert corrosion rate")
        if self._unit == other_unit: return self._value
        if self._unit == MM_PER_YR and other_unit == IN_PER_YR: return self._value / 25.4
        if self._unit == IN_PER_YR and other_unit == MM_PER_YR: return self._value * 25.4
        raise ValueError("Unhandled corrosion rate conversion")
    def __repr__(self): return f"CorrosionRate({self._value}, {self._unit!r})"


class Temperature:
    __slots__ = ("_value", "_unit")
    def __init__(self, value, unit=CELSIUS):
        self._value = float(value)
        if unit not in (CELSIUS, FAHRENHEIT): raise UnitMismatchError(f"Temperature unit must be C or F")
        self._unit = unit
    @property
    def value(self): return self._value
    @property
    def unit(self): return self._unit
    def to(self, other_unit):
        if other_unit == self._unit: return self._value
        if self._unit == CELSIUS and other_unit == FAHRENHEIT: return self._value * 9.0 / 5.0 + 32.0
        if self._unit == FAHRENHEIT and other_unit == CELSIUS: return (self._value - 32.0) * 5.0 / 9.0
        raise ValueError("Unhandled temperature conversion")
    def __repr__(self): return f"Temperature({self._value}, {self._unit!r})"


class Hardness:
    __slots__ = ("_value",)
    def __init__(self, value, unit=HB):
        if unit != HB: raise UnitMismatchError("Hardness unit must be HB")
        self._value = float(value)
    @property
    def value(self): return self._value
    @property
    def unit(self): return HB
    def __repr__(self): return f"Hardness({self._value} HB)"
