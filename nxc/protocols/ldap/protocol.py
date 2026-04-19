from __future__ import annotations

from argparse import Namespace
from typing import Any

from nxc.protocols.ldap.adws_adapter import ADWSAdapter
from nxc.protocols.ldap.directory_adapter import DirectoryAdapter, DirectorySearchRequest
from nxc.protocols.ldap.ldap_adapter import LDAPAdapter


class LDAPProtocol:
    def __init__(self, args: Namespace, ldap_impl: Any) -> None:
        self.args = args
        self._ldap_impl = ldap_impl
        self._adapter = self._build_adapter()

    def _build_adapter(self) -> DirectoryAdapter:
        if getattr(self.args, "directory_transport", "ldap") == "adws":
            return ADWSAdapter(endpoint=getattr(self.args, "adws_endpoint", None))
        return LDAPAdapter(self._ldap_impl)

    @property
    def adapter(self) -> DirectoryAdapter:
        return self._adapter

    def run_search(self, base_dn: str, ldap_filter: str, attributes: list[str] | None = None) -> list[dict[str, Any]]:
        req = DirectorySearchRequest(
            base_dn=base_dn,
            ldap_filter=ldap_filter,
            attributes=attributes,
            scope=getattr(self.args, "adws_scope", "subtree"),
            page_size=getattr(self.args, "adws_page_size", 256),
        )
        return self._adapter.search(req)
