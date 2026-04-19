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

    Deep transport/auth wire behavior is intentionally deferred.
    """

    def __init__(self, endpoint: str = "https://localhost:9389/ActiveDirectoryWebServices") -> None:
        self.session = ADWSSession(endpoint=endpoint)

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
        if self.session.auth_mode != "ntlm":
            raise NotImplementedError("Only NTLM scaffolding is implemented for ADWS")
        return {
            "enumeration_context": "ctx-1",
            "items": [],
            "end_of_sequence": True,
            "request": {
                "base_dn": base_dn,
                "ldap_filter": ldap_filter,
                "attributes": list(attributes or []),
                "scope": scope,
                "page_size": page_size,
            },
        }

    def pull(self, enumeration_context: str) -> dict[str, Any]:
        if not enumeration_context:
            raise ValueError("enumeration_context is required")
        return {"enumeration_context": enumeration_context, "items": [], "end_of_sequence": True}

    def query_rootdse(self, attrs: Iterable[str] | None = None) -> dict[str, Any]:
        requested = list(attrs or [])
        return {
            "defaultNamingContext": "DC=example,DC=com",
            "schemaNamingContext": "CN=Schema,CN=Configuration,DC=example,DC=com",
            "configurationNamingContext": "CN=Configuration,DC=example,DC=com",
            "requested": requested,
        }
