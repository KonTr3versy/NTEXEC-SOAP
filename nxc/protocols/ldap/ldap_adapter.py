from __future__ import annotations

from typing import Any, Iterable

from .directory_adapter import DirectoryAdapter, DirectorySearchRequest


class LDAPAdapter(DirectoryAdapter):
    """Thin adapter around an existing LDAP implementation object."""

    def __init__(self, ldap_impl: Any) -> None:
        self._ldap = ldap_impl

    def connect(self) -> None:
        self._ldap.connect()

    def bind_ntlm(self, username: str, password: str, domain: str | None = None) -> None:
        self._ldap.bind_ntlm(username=username, password=password, domain=domain)

    def bind_kerberos(self, principal: str, credential: Any | None = None) -> None:
        self._ldap.bind_kerberos(principal=principal, credential=credential)

    def rootdse(self, attrs: Iterable[str] | None = None) -> dict[str, Any]:
        return self._ldap.rootdse(attrs=attrs)

    def search(self, req: DirectorySearchRequest) -> list[dict[str, Any]]:
        return self._ldap.search(
            base_dn=req.base_dn,
            ldap_filter=req.ldap_filter,
            attributes=req.attributes,
            scope=req.scope,
            page_size=req.page_size,
        )
