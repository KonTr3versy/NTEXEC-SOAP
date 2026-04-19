import pytest

from nxc.protocols.ldap.directory_adapter import DirectorySearchRequest


def test_directory_search_request_defaults():
    req = DirectorySearchRequest(base_dn="DC=example,DC=com", ldap_filter="(objectClass=*)")
    assert req.scope == "subtree"
    assert req.page_size == 256


def test_directory_search_request_invalid_scope_raises():
    with pytest.raises(ValueError):
        DirectorySearchRequest(
            base_dn="DC=example,DC=com",
            ldap_filter="(objectClass=*)",
            scope="invalid",
        )
