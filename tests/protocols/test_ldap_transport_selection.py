from argparse import Namespace

from nxc.protocols.ldap import LDAPProtocol
from nxc.protocols.ldap.adws_adapter import ADWSAdapter
from nxc.protocols.ldap.ldap_adapter import LDAPAdapter


class DummyLDAPImpl:
    def connect(self):
        return None

    def bind_ntlm(self, username, password, domain=None):
        return None

    def bind_kerberos(self, principal, credential=None):
        return None

    def rootdse(self, attrs=None):
        return {"defaultNamingContext": "DC=example,DC=com"}

    def search(self, **kwargs):
        return [{"distinguishedName": "CN=User,DC=example,DC=com"}]


def test_ldap_selected_by_default():
    args = Namespace(directory_transport="ldap", adws_endpoint=None, adws_scope="subtree", adws_page_size=256)
    protocol = LDAPProtocol(args, DummyLDAPImpl())
    assert isinstance(protocol.adapter, LDAPAdapter)


def test_adws_selected_when_requested():
    args = Namespace(directory_transport="adws", adws_endpoint="https://dc:9389/ADWS", adws_scope="subtree", adws_page_size=256)
    protocol = LDAPProtocol(args, DummyLDAPImpl())
    assert isinstance(protocol.adapter, ADWSAdapter)
