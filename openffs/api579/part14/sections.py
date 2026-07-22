"""Standard structural section catalog - AISC shapes (starter set)."""

WT_SECTIONS = {
    "WT5X16.5": {"type": "WT", "A": 3140, "d": 127.0, "bf": 101.6, "tf": 9.65, "tw": 6.86,
                  "Ix": 5.97e6, "Sx": 64.1e3, "Iy": 1.78e6, "Sy": 35.0e3},
    "WT6X25": {"type": "WT", "A": 4740, "d": 152.4, "bf": 152.4, "tf": 11.0, "tw": 8.13,
               "Ix": 13.5e6, "Sx": 122e3, "Iy": 7.07e6, "Sy": 92.8e3},
    "WT4X12": {"type": "WT", "A": 2280, "d": 101.6, "bf": 76.2, "tf": 8.76, "tw": 6.35,
               "Ix": 2.6e6, "Sx": 36.6e3, "Iy": 0.85e6, "Sy": 22.3e3},
}

L_SECTIONS = {
    "L4X4X1/2": {"type": "L", "A": 2480, "r": 12.7, "Ix": 0.39e6, "Iy": 0.39e6, "Sx": 13.3e3, "Sy": 13.3e3},
    "L4X4X3/8": {"type": "L", "A": 1890, "r": 9.53, "Ix": 0.31e6, "Iy": 0.31e6, "Sx": 10.4e3, "Sy": 10.4e3},
    "L3X3X1/4": {"type": "L", "A": 968, "r": 6.35, "Ix": 0.10e6, "Iy": 0.10e6, "Sx": 4.5e3, "Sy": 4.5e3},
}

ALL_SECTIONS = {**WT_SECTIONS, **L_SECTIONS}


def get_section(designation):
    if designation not in ALL_SECTIONS:
        raise KeyError(f"Section {designation!r} not in catalog. Known: {sorted(ALL_SECTIONS.keys())}")
    return ALL_SECTIONS[designation]
