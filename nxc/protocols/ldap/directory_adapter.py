from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Protocol


_VALID_SCOPES = {"base", "onelevel", "subtree"}


@dataclass(slots=True)
class DirectorySearchRequest:
    base_dn: str
    ldap_filter: str
    attributes: Iterable[str] | None = None
    scope: str = "subtree"
    page_size: int = 256

    def __post_init__(self) -> None:
        if self.scope not in _VALID_SCOPES:
            raise ValueError(
                f"Invalid scope '{self.scope}'. Valid scopes: {sorted(_VALID_SCOPES)}"
            )
        if self.page_size <= 0:
            raise ValueError("page_size must be positive")


class DirectoryAdapter(Protocol):
    def connect(self) -> None:
        ...

    def bind_ntlm(self, username: str, password: str, domain: str | None = None) -> None:
        ...

    def bind_kerberos(self, principal: str, credential: Any | None = None) -> None:
        ...

    def rootdse(self, attrs: Iterable[str] | None = None) -> dict[str, Any]:
        ...

    def search(self, req: DirectorySearchRequest) -> list[dict[str, Any]]:
        ...
