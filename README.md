# NTEXEC-SOAP

## Step2 POC status

This repository includes a transport abstraction for LDAP directory querying with an opt-in ADWS backend POC.

### Current capability

- ADWS adapter supports NTLM-scaffold auth, rootDSE reads, and enumerate/pull-style search with pagination over a deterministic in-memory directory dataset.
- ADWS `base`, `onelevel`, and `subtree` scopes are exercised in the client filtering helpers.
- ADWS single-object retrieval is available via base-scope helper semantics (`search_single_object`).

### Current limitations

- ADWS Kerberos authentication is intentionally not implemented yet (`NotImplementedError`).
- ADWS transport framing (NMF/NNS) is still scaffold-level and does not represent full wire-protocol coverage.
- Directory querying currently uses the local mock dataset path; live ADWS SOAP transport integration is still pending.
