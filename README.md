# NTEXEC-SOAP

## Step2 POC status

This repository now includes a transport abstraction for LDAP directory querying with an opt-in ADWS backend scaffold.

### Current limitations

- ADWS Kerberos authentication is intentionally not implemented yet (`NotImplementedError`).
- ADWS transport framing (NMF/NNS) is scaffold-level and only includes minimal helper behavior.
- ADWS search currently returns normalized entries from scaffolded enumerate/pull responses; deep wire protocol support is deferred.
