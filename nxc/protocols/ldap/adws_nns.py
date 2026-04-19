from __future__ import annotations

from typing import Any


def parse_enumeration_context(payload: dict[str, Any]) -> str | None:
    """Extract the ADWS enumeration context when present."""
    return payload.get("enumeration_context")


def is_end_of_sequence(payload: dict[str, Any]) -> bool:
    """Report whether server indicated no additional pull results are available."""
    return bool(payload.get("end_of_sequence", False))
