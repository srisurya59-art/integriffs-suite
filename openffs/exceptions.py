# OpenFFS Custom Engineering Exceptions
# Objective: Clear error terminology to educate developers and users.

class EngineeringBoundaryError(Exception):
    """Raised when an engineering input falls outside physical or regulatory code limits."""
    pass
