"""Catalog of engineering standards OpenFFS tracks."""
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class StandardRecord:
    authority: str; code: str; edition: str; year: int
    expected_next_year: int; source_url: str = ""; notes: str = ""


CATALOG = [
    StandardRecord("API/ASME", "API 579-1/ASME FFS-1", "2021", 2021, 2027,
                   "https://www.api.org/products/5791-api-asme-ffs-1", "Primary FFS standard"),
    StandardRecord("API", "API 570", "2020", 2020, 2026,
                   "https://www.api.org/products/570-piping-inspection-code", "Piping inspection"),
    StandardRecord("API", "API 571", "2020", 2020, 2026,
                   "https://www.api.org/products/571-damage-mechanisms", "Damage mechanisms"),
    StandardRecord("API", "API 510", "2014+2023", 2014, 2026,
                   "https://www.api.org/products/510-pressure-vessel-inspection", "Pressure vessel inspection"),
    StandardRecord("ASME", "B31.3", "2022", 2022, 2028,
                   "https://www.asme.org/codes-standards/find-codes-standards/b31-3-process-piping", "Process piping"),
    StandardRecord("ASME", "B31.1", "2022", 2022, 2028,
                   "https://www.asme.org/codes-standards/find-codes-standards/b31-1-power-piping", "Power piping"),
    StandardRecord("ASME", "VIII-1", "2023", 2023, 2029,
                   "https://www.asme.org/codes-standards/find-codes-standards/viii-1-boiler-pressure-vessel-code", "Boiler & PV rules"),
]


def get_catalog():
    return list(CATALOG)


def find(code):
    for r in CATALOG:
        if r.code == code: return r
    return None
