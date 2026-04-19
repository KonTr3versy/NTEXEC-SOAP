You are acting as a senior offensive-security-focused software engineer reviewing the NetExec codebase.

Task:
Analyze how to add ADWS (Active Directory Web Services over TCP 9389) support to NetExec in the cleanest, lowest-risk way.

Primary requirement:
Do NOT default to creating a brand-new top-level protocol.
Your first design assumption should be that ADWS should become an alternate backend/transport under the existing LDAP protocol flow, unless the repository structure proves that is clearly impractical.

Context:
- Repository: NetExec
- Reference/oracle for feasibility and protocol ideas: SoaPy
- ADWS is not just LDAP on another port.
- For the first implementation, focus on read/query behavior only.
- Target operator experience should remain LDAP-like from the NetExec user perspective.
- Existing LDAP behavior must remain unchanged by default.
- ADWS mode must be opt-in.

What I want from you in this stage:
1. Inspect the current NetExec repository structure.
2. Identify the current LDAP protocol entry points, CLI argument definitions, connection flow, and search/result handling.
3. Find the best insertion points for a transport/backend abstraction.
4. Recommend a minimal-change design for adding ADWS support.
5. Produce a concrete implementation plan before writing major code.

Design goals:
- Preserve the current LDAP UX as much as possible
- Minimize breakage to existing modules
- Keep refactors localized
- Avoid unrelated cleanup
- Keep the first milestone small and believable

Expected architecture:
Propose a transport-neutral directory abstraction, similar to:

@dataclass
class DirectorySearchRequest:
    base_dn: str
    ldap_filter: str
    attributes: list[str]
    scope: str = "subtree"
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

Likely implementation targets:
- LDAPAdapter wrapping existing behavior
- ADWSAdapter as new backend

Potential file targets to inspect:
- nxc/protocols/ldap.py
- nxc/protocols/ldap/proto_args.py
- protocol loader / connection flow
- LDAP search/result parsing logic
- tests relevant to LDAP

ADWS-specific implementation assumptions:
- First milestone should focus on:
  - backend abstraction
  - ADWS backend skeleton
  - CLI plumbing
  - naming-context discovery scaffolding
  - enumerate/pull search scaffolding
  - result normalization scaffolding
- NTLM should be the first auth path planned
- Kerberos should be designed for, but can be staged later
- UserName/TLS endpoints should be deferred unless necessary

What NOT to do in this stage:
- Do not make broad code changes without first showing the plan
- Do not claim full ADWS support
- Do not over-scope into write operations
- Do not redesign unrelated protocols

Output format:
Please produce exactly these sections:

1. Repository findings
- Relevant files and classes
- Current LDAP flow
- CLI integration points
- Search/result handling locations

2. Recommended design
- Whether ADWS should be integrated under LDAP or separated
- Why
- Proposed abstraction and file layout

3. Implementation plan
- Ordered steps
- Risk areas
- What should be stubbed vs fully implemented first

4. Proposed file change map
- File path
- Purpose of change
- Estimated change size

5. Suggested CLI design
- Proposed flags
- Backward compatibility notes

6. Testing plan
- Unit tests
- Integration-test placeholders
- Failure-path coverage

7. Open questions / assumptions
- Anything uncertain from the codebase inspection

Important:
Bias toward a realistic NetExec-style implementation that an offensive security engineer would actually maintain.
Prefer minimal-change, high-leverage design over ambitious rewrites.
