from __future__ import annotations

from typing import Any


_ATTRIBUTE_MAP = {
    "distinguishedName": "distinguishedName",
    "sAMAccountName": "sAMAccountName",
    "objectSid": "objectSid",
    "objectGUID": "objectGUID",
    "defaultNamingContext": "defaultNamingContext",
    "schemaNamingContext": "schemaNamingContext",
    "configurationNamingContext": "configurationNamingContext",
}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def normalize_adws_entry(raw: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for src, dst in _ATTRIBUTE_MAP.items():
        if src in raw:
            value = raw[src]
            values = _as_list(value)
            normalized[dst] = values[0] if len(values) == 1 else values
    for key, value in raw.items():
        if key not in normalized:
            values = _as_list(value)
            normalized[key] = values[0] if len(values) == 1 else values
    return normalized


def normalize_adws_rootdse(raw: dict[str, Any]) -> dict[str, Any]:
    return normalize_adws_entry(raw)
