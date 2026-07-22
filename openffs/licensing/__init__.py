"""License validator. Offline-first; default tier is MIT community."""
import json, hmac, hashlib, base64, time
from pathlib import Path
from dataclasses import dataclass
from typing import FrozenSet
from openffs.core.exceptions import LicenseError


@dataclass(frozen=True)
class License:
    licensee: str; tier: str; seats: int; features: FrozenSet
    issued_at: str; expires_at: str; signature: str


DEMO_SIGNING_KEY = b"OPENFFS-DEMO-SIGNING-KEY-REPLACE-IN-PRODUCTION"
FEATURE_PRO_PARTS_FULL = "parts.full"; FEATURE_PRO_PDF = "report.pdf_branded"
FEATURE_PRO_LIVE_STANDARDS = "standards.live"


def _sign(payload):
    return base64.b64encode(hmac.new(DEMO_SIGNING_KEY, payload.encode(), hashlib.sha256).digest()).decode()


def _verify(payload, sig_b64):
    return hmac.compare_digest(_sign(payload), sig_b64)


def issue_license(licensee, tier, seats, features, expires_at="perpetual", issued_at=""):
    issued_at = issued_at or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    payload = json.dumps({"licensee": licensee, "tier": tier, "seats": seats,
        "features": sorted(features), "issued_at": issued_at, "expires_at": expires_at}, separators=(",", ":"))
    return License(licensee=licensee, tier=tier, seats=seats, features=frozenset(features),
        issued_at=issued_at, expires_at=expires_at, signature=_sign(payload))


def license_to_dict(lic):
    return {"licensee": lic.licensee, "tier": lic.tier, "seats": lic.seats,
        "features": sorted(lic.features), "issued_at": lic.issued_at,
        "expires_at": lic.expires_at, "signature": lic.signature}


def license_from_dict(d):
    payload = json.dumps({"licensee": d["licensee"], "tier": d["tier"], "seats": d["seats"],
        "features": sorted(d["features"]), "issued_at": d["issued_at"], "expires_at": d["expires_at"]}, separators=(",", ":"))
    if not _verify(payload, d.get("signature", "")):
        raise LicenseError(f"License signature invalid")
    return License(licensee=d["licensee"], tier=d["tier"], seats=d["seats"],
        features=frozenset(d["features"]), issued_at=d["issued_at"], expires_at=d["expires_at"], signature=d["signature"])


SEARCH_PATHS = [Path.cwd() / "openffs.lic", Path.home() / ".config" / "openffs" / "openffs.lic"]


def load_license(path=None):
    candidates = [Path(path)] if path else SEARCH_PATHS
    for p in candidates:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f: d = json.load(f)
                return license_from_dict(d)
            except (json.JSONDecodeError, KeyError, LicenseError): continue
    return issue_license("anonymous", "community", 1, frozenset())


def save_license(lic, path=None):
    p = Path(path) if path else SEARCH_PATHS[0]
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f: json.dump(license_to_dict(lic), f, indent=2)
    return p


def has_feature(lic, feature): return feature in lic.features or lic.tier == "enterprise"
