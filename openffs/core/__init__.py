"""Engineering Core - frozen foundational services."""
from openffs.core.exceptions import (
    OpenFFSError, ValidationError, UnitMismatchError,
    NegativeEffectiveThickness, InvalidCorrosionRate,
    InvalidGeometry, LicenseError,
)
from openffs.core.units import (
    Length, Pressure, Time, CorrosionRate, Hardness, Temperature,
    MM, IN, MPA, PSI, YEAR, MM_PER_YR, IN_PER_YR, CELSIUS, FAHRENHEIT, HB,
)
from openffs.core.quantities import (
    UniformMetalLoss, LocalMetalLoss, Gouge, Perforation, DamageType,
)
from openffs.core.validation import validate_positive, validate_non_negative, validate_range
from openffs.core.result import AssessmentResult, Suitability
from openffs.core.calculation import CalculationLog, CalculationStep
