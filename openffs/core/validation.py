"""Input validation helpers."""
from openffs.core.exceptions import ValidationError


def validate_positive(name, value):
    if value is None: raise ValidationError(f"{name} must not be None")
    if not isinstance(value, (int, float)): raise ValidationError(f"{name} must be numeric")
    if value <= 0: raise ValidationError(f"{name} must be positive, got {value}")
    return float(value)


def validate_non_negative(name, value):
    if value is None: raise ValidationError(f"{name} must not be None")
    if not isinstance(value, (int, float)): raise ValidationError(f"{name} must be numeric")
    if value < 0: raise ValidationError(f"{name} must be >= 0, got {value}")
    return float(value)


def validate_range(name, value, lo, hi, inclusive=True):
    if value is None: raise ValidationError(f"{name} must not be None")
    if not isinstance(value, (int, float)): raise ValidationError(f"{name} must be numeric")
    if inclusive:
        if value < lo or value > hi: raise ValidationError(f"{name}={value} not in [{lo}, {hi}]")
    else:
        if value <= lo or value >= hi: raise ValidationError(f"{name}={value} not in ({lo}, {hi})")
    return float(value)
