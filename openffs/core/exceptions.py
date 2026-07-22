"""Exception taxonomy for OpenFFS."""

class OpenFFSError(Exception):
    """Base class for all OpenFFS exceptions."""
    pass


class ValidationError(OpenFFSError):
    """Input failed validation."""
    pass


class UnitMismatchError(OpenFFSError):
    """Dimensional inconsistency detected."""
    pass


class NegativeEffectiveThickness(OpenFFSError):
    """Effective thickness computed as zero or negative."""

    def __init__(self, te, context=""):
        self.te = te
        msg = f"Effective thickness te={te:.4f} <= 0"
        if context:
            msg += f" ({context})"
        super().__init__(msg)


class InvalidCorrosionRate(OpenFFSError):
    """Corrosion rate must be positive for remaining-life calculation."""
    pass


class InvalidGeometry(OpenFFSError):
    """Geometry input invalid."""
    pass


class LicenseError(OpenFFSError):
    """License validation or activation failed."""
    pass
