# Step2 Execution Plan (ADWS-backed directory querying for NetExec)

## 1) Plan (8–12 bullets)

1. Add a small transport-neutral interface (`DirectorySearchRequest`, `DirectoryAdapter`) under LDAP so LDAP and ADWS can share one call shape without changing operator UX.
2. Introduce `LDAPAdapter` as a wrapper around current LDAP behavior first, and verify default path is unchanged.
3. Add `ADWSAdapter` scaffold with explicit staged TODOs for deep transport/auth pieces (don’t overclaim completeness).
4. Add backend selection in LDAP protocol flow (`ldap` default, `adws` opt-in).
5. Add CLI transport flag(s) (`--directory-transport ldap|adws` or `--adws`) plus optional ADWS tuning args.
6. Implement ADWS client scaffolding (`adws_client.py`, `adws_nmf.py`, `adws_nns.py`) with clear boundaries and narrow public API.
7. Add ADWS enumerate/pull search scaffolding and “single-object via base search” helper semantics.
8. Add ADWS normalization layer to emit LDAP-like dictionaries keyed as expected by existing modules.
9. Add focused tests for selection, CLI parsing, request object behavior, normalization, and unimplemented-path failures.
10. Finalize with honest limitations + next steps, aligned to “POC, maintainable, localized” scope.

---

## 2) File-by-file work plan

### `nxc/protocols/ldap/directory_adapter.py` (new)
**Purpose:** Shared contracts.

**Add:**
- `DirectorySearchRequest` dataclass:
  - `base_dn`, `ldap_filter`, `attributes`, `scope="subtree"`, `page_size=256`
  - validate `scope in {"base","onelevel","subtree"}`
- `DirectoryAdapter` protocol:
  - `connect()`
  - `bind_ntlm(...)`
  - `bind_kerberos(...)`
  - `rootdse(attrs)`
  - `search(req)`

**Acceptance criteria:**
- No protocol-specific code inside this file.
- Unit test validates defaults + invalid scope behavior.

---

### `nxc/protocols/ldap/ldap_adapter.py` (new)
**Purpose:** Preserve existing LDAP behavior via adapter.

**Add:**
- `class LDAPAdapter(DirectoryAdapter)` accepting existing ldap protocol state/dependencies.
- Methods delegate to existing LDAP implementation internals (or thin wrappers).

**Acceptance criteria:**
- No behavior drift for default LDAP path.
- Existing LDAP actions work unchanged when transport is `ldap`.

---

### `nxc/protocols/ldap/adws_adapter.py` (new)
**Purpose:** ADWS backend skeleton (read/query first milestone).

**Add:**
- `class ADWSAdapter(DirectoryAdapter)`
- `connect()` scaffolding to ADWS client session
- `bind_ntlm(...)` as first planned path (can be scaffold + structured TODO)
- `bind_kerberos(...)` explicit `NotImplementedError` or staged TODO if not ready
- `rootdse(attrs)` helper/scaffold for naming contexts
- `search(req)` using enumerate/pull structure (scaffold acceptable if explicit)

**Acceptance criteria:**
- Clear failure modes (`NotImplementedError`/custom errors) for deferred depth.
- No “pretend complete” behavior.

---

### `nxc/protocols/ldap/adws_client.py` (new)
**Purpose:** Orchestration boundary over ADWS wire details.

**Add:**
- Session init + endpoint parsing
- High-level methods:
  - `enumerate_search(...)`
  - `pull(...)`
  - `query_rootdse(...)`
- Returns raw structured payloads (normalization happens elsewhere)

**Acceptance criteria:**
- Small cohesive class; no LDAP business logic mixed in.

---

### `nxc/protocols/ldap/adws_nmf.py` and `nxc/protocols/ldap/adws_nns.py` (new)
**Purpose:** Transport framing scaffolding.

**Add:**
- Minimal message/frame helpers needed for POC
- Context/end-of-sequence parse helper hooks
- Explicit TODO markers for incomplete protocol depth

**Acceptance criteria:**
- Helpers are composable and testable in isolation.
- Unimplemented areas fail explicitly.

---

### `nxc/parsers/adws_results.py` (new)
**Purpose:** Normalize ADWS results into LDAP-like dictionaries.

**Add:**
- `normalize_adws_entry(raw) -> dict`
- `normalize_adws_rootdse(raw) -> dict`
- Attribute mapping:
  - `distinguishedName`, `sAMAccountName`, `objectSid`, `objectGUID`,
    `defaultNamingContext`, `schemaNamingContext`, `configurationNamingContext`

**Acceptance criteria:**
- Output shape matches existing LDAP consumer expectations.
- Handles single vs multi-valued attributes consistently.

---

### `nxc/protocols/ldap/proto_args.py` (modify)
**Purpose:** Opt-in ADWS flag plumbing.

**Add one style (recommended):**
- `--directory-transport` with choices `ldap|adws` default `ldap`
- Optional:
  - `--adws-endpoint`
  - `--adws-page-size`
  - `--adws-scope`

**Alternative:** support `--adws` as alias for `--directory-transport adws`.

**Acceptance criteria:**
- Existing invocations untouched.
- ADWS args ignored/validated appropriately unless ADWS selected.

---

### `nxc/protocols/ldap.py` (modify, localized)
**Purpose:** Backend selection + adapter-based flow.

**Refactor minimally:**
- Add backend factory:
  - if `args.directory_transport == "adws"` -> `ADWSAdapter`
  - else -> `LDAPAdapter`
- Replace direct transport calls in shared query/auth entry points with adapter calls.
- Keep existing command handlers and output UX intact.

**Acceptance criteria:**
- Default behavior equivalent to current LDAP path.
- ADWS path is clearly opt-in.

---

### Tests (`tests/...` new/updated)
**Must cover:**
- Backend selection
- Default LDAP compatibility
- CLI parsing
- `DirectorySearchRequest` behavior
- ADWS normalization
- Enumeration context/end-of-sequence helper behavior
- Graceful unimplemented transport handling

**Suggested test files:**
- `tests/protocols/test_ldap_transport_selection.py`
- `tests/protocols/test_ldap_proto_args_adws.py`
- `tests/protocols/test_directory_search_request.py`
- `tests/parsers/test_adws_results.py`
- `tests/protocols/test_adws_transport_scaffold.py`

---

## 3) Suggested sequencing

1. Contracts (`directory_adapter.py`)
2. `LDAPAdapter` wrapper
3. Backend selection in `ldap.py` (still LDAP only)
4. CLI flags
5. `ADWSAdapter` scaffold
6. ADWS client + nmf/nns helpers
7. ADWS normalization parser
8. Tests + explicit known gaps section

---

## 4) Risk controls / guardrails

- Keep all ADWS code paths behind opt-in flags.
- Avoid broad reorganization of existing LDAP handlers.
- Use explicit TODO/NotImplemented for deep unbuilt pieces.
- Add regression test that default LDAP transport behavior is unchanged.

---

## 5) Definition of Done (Step2 POC)

- Transport abstraction introduced and used.
- Default LDAP behavior unchanged.
- ADWS backend selectable via CLI.
- ADWS query/result scaffolding present with normalization.
- Tests added for selection/parsing/normalization/failure-paths.
- Limitations documented honestly (not overstated).
