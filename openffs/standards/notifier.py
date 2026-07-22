"""Standards currency notifier - offline by default."""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Callable
from openffs.standards.catalog import get_catalog


@dataclass(frozen=True)
class Notification:
    standard: str; message: str; severity: str
    action_url: Optional[str] = None


def check_currency(current_year=None, fetch_fn=None):
    year = current_year or datetime.now().year
    notifs = []
    for r in get_catalog():
        if year >= r.expected_next_year:
            notifs.append(Notification(standard=r.code,
                message=f"{r.code} expected new edition around {r.expected_next_year}; current year is {year}. Verify you are on the latest edition.",
                severity="INFO", action_url=r.source_url))
    return notifs


def format_notifications(notifs):
    if not notifs: return "All tracked standards are current."
    lines = []
    for n in notifs:
        lines.append(f"[{n.severity}] {n.message}")
        if n.action_url: lines.append(f"    info: {n.action_url}")
    return "\n".join(lines)
