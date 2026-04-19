from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(slots=True)
class ADWSSession:
    endpoint: str
    connected: bool = False
    auth_mode: str | None = None


class ADWSClient:
    """POC orchestration layer for ADWS operations.

    This client now supports deterministic enumerate/pull behavior over a simple
    in-memory dataset so the ADWS path can be exercised end-to-end in tests.
    """

    def __init__(self, endpoint: str = "https://localhost:9389/ActiveDirectoryWebServices") -> None:
        self.session = ADWSSession(endpoint=endpoint)
        self._directory_rows: list[dict[str, Any]] = []
        self._contexts: dict[str, list[dict[str, Any]]] = {}
        self._context_counter = 0

    def load_mock_directory(self, rows: Iterable[dict[str, Any]]) -> None:
        """Load directory entries used by enumerate/pull methods.

        This is intentionally test-friendly scaffolding until wire-level ADWS
        integration lands.
        """
        self._directory_rows = [dict(row) for row in rows]

    def connect(self) -> None:
        self.session.connected = True

    def bind_ntlm(self, username: str, password: str, domain: str | None = None) -> None:
        if not self.session.connected:
            raise RuntimeError("ADWS session is not connected")
        if not username or not password:
            raise ValueError("username and password are required")
        self.session.auth_mode = "ntlm"

    def enumerate_search(
        self,
        *,
        base_dn: str,
        ldap_filter: str,
        attributes: Iterable[str] | None,
        scope: str,
        page_size: int,
    ) -> dict[str, Any]:
        self._validate_ready()

        matching = self._filter_rows(
            base_dn=base_dn,
            ldap_filter=ldap_filter,
            scope=scope,
            attributes=attributes,
        )
        chunk, remainder = matching[:page_size], matching[page_size:]

        context: str | None = None
        if remainder:
            context = self._new_context(remainder)

        return {
            "enumeration_context": context,
            "items": chunk,
            "end_of_sequence": context is None,
            "request": {
                "base_dn": base_dn,
                "ldap_filter": ldap_filter,
                "attributes": list(attributes or []),
                "scope": scope,
                "page_size": page_size,
            },
        }

    def pull(self, enumeration_context: str, page_size: int = 256) -> dict[str, Any]:
        self._validate_ready()
        if not enumeration_context:
            raise ValueError("enumeration_context is required")

        remaining = self._contexts.get(enumeration_context)
        if remaining is None:
            raise ValueError(f"Unknown enumeration_context: {enumeration_context}")

        chunk, remainder = remaining[:page_size], remaining[page_size:]
        if remainder:
            self._contexts[enumeration_context] = remainder
        else:
            del self._contexts[enumeration_context]

        return {
            "enumeration_context": enumeration_context if remainder else None,
            "items": chunk,
            "end_of_sequence": not remainder,
        }

    def query_rootdse(self, attrs: Iterable[str] | None = None) -> dict[str, Any]:
        requested = list(attrs or [])
        data = {
            "defaultNamingContext": "DC=example,DC=com",
            "schemaNamingContext": "CN=Schema,CN=Configuration,DC=example,DC=com",
            "configurationNamingContext": "CN=Configuration,DC=example,DC=com",
        }
        if requested:
            return {key: value for key, value in data.items() if key in requested}
        return data

    def _validate_ready(self) -> None:
        if not self.session.connected:
            raise RuntimeError("ADWS session is not connected")
        if self.session.auth_mode != "ntlm":
            raise NotImplementedError("Only NTLM scaffolding is implemented for ADWS")

    def _new_context(self, entries: list[dict[str, Any]]) -> str:
        self._context_counter += 1
        context = f"ctx-{self._context_counter}"
        self._contexts[context] = entries
        return context

    def _filter_rows(
        self,
        *,
        base_dn: str,
        ldap_filter: str,
        scope: str,
        attributes: Iterable[str] | None,
    ) -> list[dict[str, Any]]:
        selected = [row for row in self._directory_rows if self._within_scope(row, base_dn, scope)]

        if ldap_filter and ldap_filter != "(objectClass=*)":
            selected = [row for row in selected if self._match_filter(row, ldap_filter)]

        attrs = list(attributes or [])
        if attrs:
            selected = [self._select_attributes(row, attrs) for row in selected]

        return selected

    def _within_scope(self, row: dict[str, Any], base_dn: str, scope: str) -> bool:
        dn = str(row.get("distinguishedName", ""))
        dn_lower = dn.lower()
        base_lower = base_dn.lower()

        if scope == "base":
            return dn_lower == base_lower
        if scope == "subtree":
            return dn_lower == base_lower or dn_lower.endswith("," + base_lower)
        if scope == "onelevel":
            if not dn_lower.endswith("," + base_lower):
                return False
            # Count RDN components above base.
            return dn_lower.count(",") == base_lower.count(",") + 1
        return False

    def _match_filter(self, row: dict[str, Any], ldap_filter: str) -> bool:
        # Supported subset: (attr=value)
        filter_text = ldap_filter.strip()
        if not (filter_text.startswith("(") and filter_text.endswith(")")):
            return False
        body = filter_text[1:-1]
        if "=" not in body:
            return False

        attr, value = body.split("=", 1)
        current = row.get(attr)
        if current is None:
            return False
        if isinstance(current, list):
            return any(str(v).lower() == value.lower() for v in current)
        return str(current).lower() == value.lower()

    def _select_attributes(self, row: dict[str, Any], attrs: list[str]) -> dict[str, Any]:
        # Include DN even when not explicitly requested, matching LDAP-ish behavior.
        keep = set(attrs) | {"distinguishedName"}
        return {k: v for k, v in row.items() if k in keep}
