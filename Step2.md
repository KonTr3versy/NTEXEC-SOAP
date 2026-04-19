You are now implementing the approved design for adding ADWS-backed directory querying to NetExec.

Goal:
Build a proof-of-concept branch that adds ADWS as an alternate backend/transport for the existing LDAP protocol flow.

Important constraints:
- Existing LDAP behavior must remain unchanged by default
- ADWS mode must be opt-in
- Keep changes localized
- Do not overstate implementation completeness
- Prioritize a believable, maintainable prototype over a sprawling partial implementation

Implementation scope for this pass:
1. Refactor the LDAP protocol flow to support a backend/transport abstraction
2. Add an ADWS backend skeleton and wire it into the LDAP flow
3. Add CLI options for selecting ADWS
4. Add ADWS query/result normalization scaffolding
5. Add tests for backend selection, parser behavior, and CLI handling
6. Add explicit TODOs where deep protocol work is not yet complete

Architecture target:
Use a transport-neutral interface such as:

@dataclass
class DirectorySearchRequest:
    base_dn: str
    ldap_filter: str
    attributes: list[str]
    scope: str = "subtree"   # base | onelevel | subtree
    page_size: int = 256

class DirectoryAdapter(Protocol):
    def connect(self) -> None: ...
    def bind_ntlm(self, domain: str, username: str, password: str | None = None,
                  nt_hash: str | None = None) -> None: ...
    def bind_kerberos(self, domain: str, username: str, password: str | None = None,
                      nt_hash: str | None = None, aes_key: str | None = None,
                      kdc_host: str | None = None, use_cache: bool = False) -> None: ...
    def rootdse(self, attrs: list[str]) -> dict[str, Any]: ...
    def search(self, req: DirectorySearchRequest) -> Iterable[dict[str, Any]]: ...

Implement:
- LDAPAdapter that wraps or reuses current LDAP behavior
- ADWSAdapter that provides the new backend surface

Recommended files to create or modify:
- nxc/protocols/ldap.py
- nxc/protocols/ldap/proto_args.py
- nxc/protocols/ldap/adws_client.py
- nxc/protocols/ldap/adws_nmf.py
- nxc/protocols/ldap/adws_nns.py
- nxc/parsers/adws_results.py
- tests/... relevant new or updated test files

CLI behavior:
Support one of the following, based on existing NetExec style:
- --adws
or
- --directory-transport ldap|adws

Optional supportive args:
- --adws-page-size
- --adws-scope
- --adws-endpoint

ADWS behavior expectations for this pass:
- Search path should be designed around enumerate/pull semantics
- “Get one object” should reuse search with:
  - base_dn = DN or GUID
  - ldap_filter = (objectClass=*)
  - scope = base
  - page_size = 1
- RootDSE/naming-context discovery should have a dedicated helper or scaffold
- Normalize returned objects into LDAP-like dictionaries with keys such as:
  - distinguishedName
  - sAMAccountName
  - objectSid
  - objectGUID
  - defaultNamingContext
  - schemaNamingContext
  - configurationNamingContext

Implementation strategy:
Phase 1 for this coding pass should be:
- introduce the abstraction
- preserve current LDAP backend behavior
- add ADWS backend scaffold
- add parser/normalization layer
- add CLI selection
- add tests
- add explicit TODOs for live NTLM/Kerberos transport completion if not fully implemented

Code quality requirements:
- Keep classes small and cohesive
- Add docstrings where behavior is non-obvious
- Do not add dead code just to look complete
- Use explicit NotImplementedError or custom errors where functionality is intentionally deferred
- Make failure modes clear and structured
- Keep comments honest and technically precise

Testing requirements:
Add tests for:
- backend selection
- backward compatibility of default LDAP path
- CLI parsing of ADWS flags
- DirectorySearchRequest behavior
- ADWS result normalization
- enumeration context / end-of-sequence parsing helpers
- graceful handling of unimplemented deep transport pieces

Expected deliverables:
1. A concise implementation summary
2. The file-by-file change list
3. The code changes
4. Tests
5. Known limitations / next steps
6. Example CLI usage

Output instructions:
- First, restate the implementation plan in 8–12 bullets max
- Then make the code changes
- Then show the patch or file diffs
- Then explain key design decisions
- Then list known gaps honestly

Important:
I would rather receive:
- a correct backend abstraction
- preserved LDAP compatibility
- a clean ADWS scaffold
- believable parser/normalization logic
- good tests
- explicit TODOs

than:
- a messy, overstated, half-working “full ADWS implementation.”

Bias toward code that fits NetExec’s existing style and is realistic for offensive-security tooling maintenance.
