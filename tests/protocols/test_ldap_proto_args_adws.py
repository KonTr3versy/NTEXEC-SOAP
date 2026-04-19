import argparse

import pytest

from nxc.protocols.ldap.proto_args import normalize_ldap_args, register_ldap_proto_args


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    register_ldap_proto_args(p)
    return p


def test_defaults_to_ldap_transport():
    args = parser().parse_args([])
    args = normalize_ldap_args(args)
    assert args.directory_transport == "ldap"


def test_adws_alias_sets_transport():
    args = parser().parse_args(["--adws"])
    args = normalize_ldap_args(args)
    assert args.directory_transport == "adws"


def test_adws_page_size_validation():
    args = parser().parse_args(["--directory-transport", "adws", "--adws-page-size", "0"])
    with pytest.raises(ValueError):
        normalize_ldap_args(args)
