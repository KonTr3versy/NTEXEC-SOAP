import pytest

from nxc.protocols.ldap.adws_adapter import ADWSAdapter
from nxc.protocols.ldap.adws_nmf import decode_frame, encode_frame
from nxc.protocols.ldap.adws_nns import is_end_of_sequence, parse_enumeration_context
from nxc.protocols.ldap.directory_adapter import DirectorySearchRequest


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


def test_adws_search_scaffold_returns_normalized_list():
    adapter = ADWSAdapter()
    adapter.connect()
    adapter.bind_ntlm("jdoe", "password", "EXAMPLE")
    req = DirectorySearchRequest(base_dn="DC=example,DC=com", ldap_filter="(objectClass=*)")
    assert adapter.search(req) == []
