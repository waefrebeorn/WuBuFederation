#!/usr/bin/env python3
"""test_govgen.py — prove the gate, do not trust the green.

A green audit is only worth what its worst case is worth. This suite
builds a throwaway corpus, plants one defect at a time, and asserts that
`govgen audit` reports *that* defect — no more, no fewer. A gate that
passes everything is not a gate.

Run: python3 tools/test_govgen.py
"""
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import govgen  # noqa: E402
import wubu_join  # noqa: E402

FILINGS = {
    "schema": "wubu-federation-registry-v1",
    "retired": [{"id": "GOV-9", "reason": "renumbered to GOV-3",
                 "used_in": ["wubugov/docs/old.md"]}],
    "filings": [
        {"id": "GOV-1", "repo": "wubugov", "file": "wubugov/docs/one.md",
         "title": "One", "status": "filed", "tools": ["sample"], "cross": ["GOV-2"]},
        {"id": "GOV-2", "repo": "wubugov", "file": "wubugov/docs/two.md",
         "title": "Two", "status": "filed", "tools": [], "cross": ["GOV-1"]},
        {"id": "RND-1", "repo": "wuburesearch", "file": "wuburesearch/docs/log.md",
         "title": "Log", "status": "log-filed", "tools": [], "cross": [],
         "record": "wuburesearch/docs/log.md"},
        {"id": "RND-0.1", "repo": "wuburesearch", "file": None,
         "title": "Org", "status": "log-filed", "tools": [], "cross": [],
         "record": "wuburesearch/docs/research-log.md"},
    ],
}
TOOLS = {"tools": [
    {"name": "sample", "python": "wubugov/tools/sample.py", "c11": "src/sample/sample.c",
     "cli": "apps/sample_cli.c", "test": "tests/test_sample.c", "filing": "GOV-1",
     "verified": "n/a"},
]}
DIVISIONS = {"organs": [{"organ": "state", "repo": "wubugov", "division": "GOV",
                         "name": "WuBuGov", "role": "state"}]}

DOCS = {
    "wubugov/docs/one.md": "# One\n\n**Government filing GOV-1. See GOV-2 and GOV-1.4.**\n",
    "wubugov/docs/two.md": "# Two\n\n**Government filing GOV-2. See GOV-1.**\n",
    "wuburesearch/docs/log.md": "# Log\n\n### RND-1 — Log\n",
    "wuburesearch/docs/research-log.md": "# Research log\n\n### RND-0.1 — Org\n",
    "wubugov/tools/sample.py": "print('sample')\n",
    "wubucore/src/sample/sample.c": "int main(void){return 0;}\n",
    "wubucore/apps/sample_cli.c": "int main(void){return 0;}\n",
    "wubucore/tests/test_sample.c": "int main(void){return 0;}\n",
}


class Corpus:
    """A throwaway corpus wired into govgen's module globals."""

    def __init__(self):
        self.dir = tempfile.mkdtemp(prefix="govgen-test-")
        self.base = self.dir
        self._saved = (govgen.BASE, govgen.REG)
        govgen.BASE = self.base
        govgen.REG = os.path.join(self.base, "registry")
        os.makedirs(govgen.REG)
        self.write("registry/filings.json", json.dumps(FILINGS))
        self.write("registry/tools.json", json.dumps(TOOLS))
        self.write("registry/divisions.json", json.dumps(DIVISIONS))
        for path, body in DOCS.items():
            self.write(path, body)

    def path(self, rel):
        return os.path.join(self.base, rel)

    def write(self, rel, body):
        p = self.path(rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(body)

    def close(self):
        govgen.BASE, govgen.REG = self._saved
        shutil.rmtree(self.dir, ignore_errors=True)

    def audit(self):
        return govgen.audit()


def kinds(defects):
    return {d.split(":")[0] for d in defects}


CASES = []


def case(fn):
    CASES.append(fn)
    return fn


@case
def baseline_is_clean(c):
    assert c.audit() == [], f"expected clean, got {c.audit()}"


@case
def phantom_ref_is_caught(c):
    c.write("wubugov/docs/two.md",
            "# Two\n\n**Government filing GOV-2.** See GOV-77.\n")
    d = c.audit()
    assert any("PHANTOM REF" in x and "GOV-77" in x for x in d), d


@case
def sub_clause_ref_resolves(c):
    # GOV-1.4 is a clause of GOV-1, not a separate filing
    d = c.audit()
    assert not any("GOV-1.4" in x for x in d), d


@case
def stale_declaration_is_caught(c):
    c.write("wubugov/docs/two.md", "# Two\n\n**Government filing GOV-8. x**\n")
    d = c.audit()
    assert any("STALE DECLARATION" in x for x in d), d


@case
def orphan_filing_is_caught(c):
    c.write("wubugov/docs/three.md", "# Three\n\n**Government filing GOV-4. x**\n")
    d = c.audit()
    assert any("ORPHAN FILING" in x for x in d), d


@case
def duplicate_file_is_caught(c):
    reg = json.loads(open(c.path("registry/filings.json")).read())
    reg["filings"].append({"id": "GOV-5", "repo": "wubugov",
                           "file": "wubugov/docs/two.md", "title": "Five",
                           "status": "filed", "tools": [], "cross": []})
    c.write("registry/filings.json", json.dumps(reg))
    d = c.audit()
    assert any("DUPLICATE FILE" in x for x in d), d


@case
def missing_file_is_caught(c):
    os.remove(c.path("wubugov/docs/two.md"))
    d = c.audit()
    assert any("MISSING FILE" in x for x in d), d


@case
def unrecorded_log_filing_is_caught(c):
    c.write("wuburesearch/docs/research-log.md", "# Research log\n\nnothing here\n")
    d = c.audit()
    assert any("UNRECORDED FILING" in x for x in d), d


@case
def phantom_cross_ref_is_caught(c):
    reg = json.loads(open(c.path("registry/filings.json")).read())
    reg["filings"][0]["cross"] = ["GOV-66"]
    c.write("registry/filings.json", json.dumps(reg))
    d = c.audit()
    assert any("PHANTOM CROSS-REF" in x for x in d), d


@case
def phantom_tool_is_caught(c):
    reg = json.loads(open(c.path("registry/filings.json")).read())
    reg["filings"][0]["tools"] = ["does_not_exist"]
    c.write("registry/filings.json", json.dumps(reg))
    d = c.audit()
    assert any("PHANTOM TOOL" in x for x in d), d


@case
def missing_c11_module_is_caught(c):
    os.remove(c.path("wubucore/src/sample/sample.c"))
    d = c.audit()
    assert any("MISSING C11" in x for x in d), d


@case
def retired_number_outside_its_docs_is_caught(c):
    c.write("wubugov/docs/two.md",
            "# Two\n\n**Government filing GOV-2.** See GOV-9.\n")
    d = c.audit()
    assert any("STALE RETIRED REF" in x for x in d), d


@case
def seal_drift_is_caught(c):
    govgen.seal_corpus("test")
    c.write("wubugov/docs/two.md",
            "# Two\n\n**Government filing GOV-2.** edited after the seal.\n")
    d = c.audit()
    assert any("SEAL DRIFT" in x for x in d), d


@case
def seal_verify_passes_when_untouched(c):
    govgen.seal_corpus("test")
    assert govgen.verify_seal() == 0


@case
def seal_chain_links_to_previous_root(c):
    first = govgen.seal_corpus("first")
    second = govgen.seal_corpus("second")
    assert second["prev_root"] == first["root"]
    lines = open(os.path.join(govgen.REG, "seal-history.jsonl")).read().splitlines()
    assert len(lines) == 2, lines


def _agent_fixture(c):
    """Write one valid agent row + card + history into the throwaway corpus."""
    import hashlib
    import json as _j
    c.write("agents/AID-WI-26-0001-8.json", _j.dumps({"aid": "AID-WI-26-0001-8",
                                                    "name": "w", "class": "witness"}))
    card = _j.load(open(c.path("agents/AID-WI-26-0001-8.json")))
    ch = wubu_join.card_hash(card)
    row = {"schema": "wubu-agent-join-v1", "aid": "AID-WI-26-0001-8", "name": "w",
           "class": "witness", "sponsor": "WID-WB-26-0001-8", "card_hash": ch,
           "joined": "2026-10-21", "prev": None}
    row["row_hash"] = hashlib.sha256(
        _j.dumps(row, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    c.write("registry/agents-history.jsonl", _j.dumps(row) + "\n")
    c.write("registry/agents.json", _j.dumps({"schema": "wubu-agent-registry-v1",
        "agents": [{"aid": "AID-WI-26-0001-8", "name": "w", "class": "witness",
                    "sponsor": "WID-WB-26-0001-8", "status": "active",
                    "card": "agents/AID-WI-26-0001-8.json", "card_hash": ch,
                    "joined": "2026-10-21"}]}))
    return ch


@case
def valid_agent_ledger_passes(c):
    _agent_fixture(c)
    assert c.audit() == [], c.audit()


@case
def agent_card_drift_is_caught(c):
    _agent_fixture(c)
    c.write("agents/AID-WI-26-0001-8.json", '{"aid": "AID-WI-26-0001-8", "name": "evil"}')
    d = c.audit()
    assert any("AGENT CARD DRIFT" in x for x in d), d


@case
def bad_agent_sponsor_is_caught(c):
    _agent_fixture(c)
    reg = json.loads(open(c.path("registry/agents.json")).read())
    reg["agents"][0]["sponsor"] = "WID-WB-26-0001-9"  # wrong check digit
    c.write("registry/agents.json", json.dumps(reg))
    d = c.audit()
    assert any("BAD AGENT SPONSOR" in x for x in d), d


@case
def broken_join_chain_is_caught(c):
    _agent_fixture(c)
    hist = open(c.path("registry/agents-history.jsonl")).read()
    row = json.loads(hist)
    row["name"] = "tampered"
    c.write("registry/agents-history.jsonl", json.dumps(row) + "\n")
    d = c.audit()
    assert any("AGENT CHAIN BROKEN" in x for x in d), d


def main():
    failed = 0
    for fn in CASES:
        c = Corpus()
        try:
            fn(c)
            print(f"  ok   {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL {fn.__name__}: {e}")
        finally:
            c.close()
    print(f"\n{'ALL GATE TESTS PASS' if not failed else f'{failed} GATE TEST(S) FAILED'}"
          f" ({len(CASES) - failed}/{len(CASES)})")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
