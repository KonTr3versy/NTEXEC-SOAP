from __future__ import annotations

from typing import Any, Iterable

from nxc.parsers.adws_results import normalize_adws_entry, normalize_adws_rootdse

from .adws_client import ADWSClient
from .adws_nns import is_end_of_sequence, parse_enumeration_context
from .directory_adapter import DirectoryAdapter, DirectorySearchRequest


class ADWSAdapter(DirectoryAdapter):
    """ADWS backend scaffold for directory querying.

    This class intentionally leaves deep protocol/auth coverage for later phases.
    """

    def __init__(self, endpoint: str | None = None) -> None:
        self._client = ADWSClient(endpoint=endpoint or "https://localhost:9389/ActiveDirectoryWebServices")

    def connect(self) -> None:
        self._client.connect()

    def bind_ntlm(self, username: str, password: str, domain: str | None = None) -> None:
        self._client.bind_ntlm(username=username, password=password, domain=domain)

    def bind_kerberos(self, principal: str, credential: Any | None = None) -> None:
        raise NotImplementedError("ADWS kerberos bind is not implemented in this POC")

    def rootdse(self, attrs: Iterable[str] | None = None) -> dict[str, Any]:
        raw = self._client.query_rootdse(attrs=attrs)
        return normalize_adws_rootdse(raw)

    def search(self, req: DirectorySearchRequest) -> list[dict[str, Any]]:
        enum_result = self._client.enumerate_search(
            base_dn=req.base_dn,
            ldap_filter=req.ldap_filter,
            attributes=req.attributes,
            scope=req.scope,
            page_size=req.page_size,
        )
        items = list(enum_result.get("items", []))
        context = parse_enumeration_context(enum_result)

        while context and not is_end_of_sequence(enum_result):
            enum_result = self._client.pull(context)
            items.extend(enum_result.get("items", []))
            context = parse_enumeration_context(enum_result)

        return [normalize_adws_entry(entry) for entry in items]
