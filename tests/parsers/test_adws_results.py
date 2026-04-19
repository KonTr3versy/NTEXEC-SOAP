from nxc.parsers.adws_results import normalize_adws_entry, normalize_adws_rootdse


def test_normalize_adws_entry_handles_single_and_multi_value_attributes():
    raw = {
        "distinguishedName": ["CN=User,DC=example,DC=com"],
        "sAMAccountName": "jdoe",
        "memberOf": ["CN=Group1", "CN=Group2"],
    }

    normalized = normalize_adws_entry(raw)
    assert normalized["distinguishedName"] == "CN=User,DC=example,DC=com"
    assert normalized["sAMAccountName"] == "jdoe"
    assert normalized["memberOf"] == ["CN=Group1", "CN=Group2"]


def test_normalize_adws_rootdse_passthrough_mapping():
    raw = {"defaultNamingContext": "DC=example,DC=com"}
    normalized = normalize_adws_rootdse(raw)
    assert normalized["defaultNamingContext"] == "DC=example,DC=com"
