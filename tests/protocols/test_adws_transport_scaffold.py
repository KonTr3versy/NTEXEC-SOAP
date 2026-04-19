import pytest

from nxc.protocols.ldap.adws_adapter import ADWSAdapter
from nxc.protocols.ldap.adws_nmf import decode_frame, encode_frame
from nxc.protocols.ldap.adws_nns import is_end_of_sequence, parse_enumeration_context
from nxc.protocols.ldap.directory_adapter import DirectorySearchRequest


MOCK_DIRECTORY = [
    {
        "distinguishedName": "CN=Jane Doe,OU=Users,DC=example,DC=com",
        "sAMAccountName": "jdoe",
        "objectClass": "user",
    },
    {
        "distinguishedName": "CN=John Smith,OU=Users,DC=example,DC=com",
        "sAMAccountName": "jsmith",
        "objectClass": "user",
    },
    {
        "distinguishedName": "CN=Srv-01,OU=Servers,DC=example,DC=com",
        "sAMAccountName": "srv01$",
        "objectClass": "computer",
    },
]


def _build_adapter() -> ADWSAdapter:
    adapter = ADWSAdapter()
    adapter._client.load_mock_directory(MOCK_DIRECTORY)  # test harness scaffold
    adapter.connect()
    adapter.bind_ntlm("jdoe", "password", "EXAMPLE")
    return adapter


def test_adws_kerberos_not_implemented():
    adapter = ADWSAdapter()
    with pytest.raises(NotImplementedError):
        adapter.bind_kerberos("user@EXAMPLE.COM")


def test_nmf_encode_decode_round_trip():
    raw = encode_frame(b"abc", end_of_sequence=True)
    frame = decode_frame(raw)
    assert frame.payload == b"abc"
    assert frame.is_end_of_sequence is True


def test_nns_helpers():
    payload = {"enumeration_context": "ctx-1", "end_of_sequence": False}
    assert parse_enumeration_context(payload) == "ctx-1"
    assert is_end_of_sequence(payload) is False


def test_adws_search_returns_entries_across_pull_pages():
    adapter = _build_adapter()
    req = DirectorySearchRequest(
        base_dn="DC=example,DC=com",
        ldap_filter="(objectClass=*)",
        scope="subtree",
        page_size=2,
    )
    results = adapter.search(req)
    assert len(results) == 3


def test_adws_search_single_object_base_scope_helper():
    adapter = _build_adapter()
    result = adapter.search_single_object("CN=Jane Doe,OU=Users,DC=example,DC=com", attributes=["sAMAccountName"])
    assert result == {
        "distinguishedName": "CN=Jane Doe,OU=Users,DC=example,DC=com",
        "sAMAccountName": "jdoe",
    }


def test_adws_search_supports_simple_attribute_filter():
    adapter = _build_adapter()
    req = DirectorySearchRequest(
        base_dn="OU=Users,DC=example,DC=com",
        ldap_filter="(sAMAccountName=jsmith)",
        scope="subtree",
        page_size=10,
    )
    results = adapter.search(req)
    assert len(results) == 1
    assert results[0]["sAMAccountName"] == "jsmith"
