#!/usr/bin/env python3
"""
govgen.py — the WuBu government generator + auditor.

The space is a registry, not a pile of markdown. This tool is the
machine that keeps it honest:

  govgen audit    — cross-check the registry against the corpus
                    (phantom refs, missing files, missing tools,
                    unverified claims). Exit 1 on any defect.
  govgen index    — regenerate every repo README doc table + the
                    master INDEX.md from registry/filings.json.
  govgen map      — regenerate the society map (WuBuCitizen REG-4)
                    from the registry.
  govgen stats    — counts per division, tool coverage, test suites.
  govgen check    — run all checks (audit + build + test) end-to-end.

Rule of the space: the registry is the single source of truth. All
indexes are GENERATED, never hand-maintained. If a doc disagrees with
the registry, the doc is wrong — and the audit will say so.
"""
import json, os, re, subprocess, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(BASE, "registry")

# ────────────────────────────────────────────────────────────── load ──
def load(name):
    with open(os.path.join(REG, name)) as f:
        return json.load(f)

def get_filings():
    return load("filings.json")["filings"]

def get_tools():
    return load("tools.json")["tools"]

def get_divisions():
    return load("divisions.json")

# ──────────────────────────────────────────────────────────── helpers ──
def repo_path(repo):
    return os.path.join(BASE, repo)

def read_doc(repo, file):
    """Read a filing document. A filing may have NO dedicated document
    (file is None) when its record is a research-log entry — see
    `record` in the registry schema."""
    if not file:
        return None
    # If file already contains the repo prefix, don't double it
    if repo and file.startswith(repo + '/'):
        p = os.path.join(BASE, file)
    else:
        p = os.path.join(repo_path(repo), file)
    if os.path.exists(p):
        with open(p) as f:
            return f.read()
    return None


def read_record(rel):
    """Read a record file (repo-relative from BASE)."""
    if not rel:
        return None
    p = os.path.join(BASE, rel)
    if os.path.exists(p):
        with open(p) as f:
            return f.read()
    return None


# A filing's own declaration: "# REG-4 — Title" in the H1, or a bolded
# "Government filing GOV-x / R&D filing RND-x / Amendment GOV-2" line.
DECL_H1 = re.compile(r'^#\s+\**((?:GOV|RND|REG|ECO|WBI|AUD|CER|DOC|TL)-\d+(?:\.\d+)?)\b', re.M)
DECL_BOLD = re.compile(
    r'\b\*{0,2}(?:Government|R&D|Economics|Audit|Constitutional|Amendment|Registry|'
    r'Research|Bureau|State|Ledger)\s+filing\s+\**((?:GOV|RND|REG|ECO|WBI|AUD|CER|DOC|TL)-\d+(?:\.\d+)?)',
    re.I)
DECL_FORM = re.compile(r'\b(?:Form|Amendment)\s+\**((?:GOV|RND|REG|ECO|WBI|AUD|CER|DOC|TL)-\d+(?:\.\d+)?)')

# ─────────────────────────────────────────────────────────────── audit ──
def audit():
    """Cross-check registry against the corpus. Return list of defects."""
    defects = []
    filings = get_filings()
    tools = get_tools()
    divisions = get_divisions()["organs"]
    retired = load("filings.json").get("retired", [])
    retired_ids = {r["id"]: r for r in retired}

    # Precompute the full id set FIRST so cross-refs resolve in any order.
    seen_ids = {}
    for f in filings:
        if f["id"] in seen_ids:
            defects.append(f"COLLISION: filing id {f['id']} used by both "
                           f"{seen_ids[f['id']]} and {f['repo']}/{f['file']}")
        seen_ids[f['id']] = f"{f['repo']}/{f['file']}"

    def resolves(tok):
        """True if tok (or its base, or a sub-clause of a real filing) resolves."""
        if tok in seen_ids:
            return True
        # sub-clause: GOV-1.4 → GOV-1
        base = re.sub(r'\.\d+$', '', tok)
        if base in seen_ids:
            return True
        # retired numbers are historical, allowed only in their used_in files
        if tok in retired_ids:
            return True
        return False

    # Log-recorded filings share one record file on purpose; dedicated
    # documents must not be shared by two filings.
    SHARED_OK = {"cross-file", "reserved", "log-filed", "cited"}
    file_owner = {}
    for f in filings:
        fp = f.get("file")
        if not fp or f.get("status") in SHARED_OK:
            continue
        if fp in file_owner:
            defects.append(
                f"DUPLICATE FILE: {fp} claims to be both {file_owner[fp]} and {f['id']}")
        else:
            file_owner[fp] = f["id"]

    for f in filings:
        # 1. file exists — a dedicated doc, or a record file holding the entry
        if f.get("file"):
            if not read_doc(f["repo"], f["file"]):
                defects.append(f"MISSING FILE: {f['id']} → {f['repo']}/{f['file']} not found")
        elif f.get("record") or f.get("evidence"):
            # `record` = a log entry that IS the filing's only document.
            # `evidence` = a historical citation proving the number was used
            # (status "cited": no standalone document survives).
            src = f.get("record") or f.get("evidence")
            rec = read_record(src)
            if rec is None:
                defects.append(f"MISSING RECORD: {f['id']} → {src} not found")
            elif f["id"] not in rec:
                defects.append(
                    f"UNRECORDED FILING: {f['id']} claims a record in "
                    f"{src} but the file never mentions it")
        else:
            defects.append(f"NO DOCUMENT: {f['id']} has neither file nor record")
        # 1b. the doc must declare its own number (identity, not just existence)
        doc = read_doc(f["repo"], f["file"])
        if doc:
            head = "\n".join(doc.splitlines()[:15])
            h1 = DECL_H1.search(head)
            bold = DECL_BOLD.search(head) or DECL_FORM.search(head)
            declared = (h1.group(1) if h1 else None) or (bold.group(1) if bold else None)
            if declared and declared.upper() != f["id"].upper():
                defects.append(
                    f"STALE DECLARATION: {f['file']} is registered as {f['id']} "
                    f"but declares itself {declared.upper()}")
        # 2. cross-refs resolve
        for x in f.get("cross", []):
            if not resolves(x):
                defects.append(f"PHANTOM CROSS-REF: {f['id']} cross-refs {x} which is not a filing")
        # 3. amendments point at existing filings
        for a in f.get("amended_by", []):
            if a not in seen_ids:
                defects.append(f"PHANTOM AMENDMENT: {f['id']} amended_by {a} which is not a filing")
        # 4. tools exist
        for t in f.get("tools", []):
            if t not in [x["name"] for x in tools]:
                defects.append(f"PHANTOM TOOL: {f['id']} claims tool {t} not in registry")

    # 6. every tool's c11 module + cli + test exists
    for t in tools:
        core = repo_path("wubucore")
        for key in ("c11", "cli"):
            if t[key]:
                p = os.path.join(core, t[key])
                if not os.path.exists(p):
                    defects.append(f"MISSING C11 {key.upper()}: {t['name']} → {t[key]}")
        if t["test"]:
            p = os.path.join(core, t["test"])
            if not os.path.exists(p):
                defects.append(f"MISSING TEST: {t['name']} → {t['test']}")
        if t["python"]:
            p = os.path.join(BASE, t["python"])
            if not os.path.exists(p):
                defects.append(f"MISSING PYTHON: {t['name']} → {t['python']}")

    # 7. corpus scan: every GOV-/RND-/ECO-/REG- id mentioned in docs must resolve
    id_set = set(seen_ids.keys())
    # 8. the seal: every sealed document must still hash to its sealed value.
    #    A filing that changed without a reseal is doc drift — the registry
    #    and the corpus have silently diverged. Fix: reseal on purpose.
    seal = load_seal()
    if seal:
        for e in seal["entries"]:
            p = os.path.join(BASE, e["file"])
            if not os.path.exists(p):
                defects.append(f"SEAL GONE: {e['id']} → {e['file']} was sealed and is now missing")
                continue
            h = sha256(p)
            if h != e["sha256"]:
                defects.append(
                    f"SEAL DRIFT: {e['file']} ({e['id']}) changed since the seal "
                    f"— run `govgen seal` to record the change")

    for repo, _, files in os.walk(BASE):
        rel = os.path.relpath(repo, BASE)
        if rel.startswith(".") or rel == "registry" or rel == "wubucore":
            continue
        for fn in files:
            if not fn.endswith(".md"):
                continue
            p = os.path.join(repo, fn)
            relpath = os.path.join(rel, fn)
            with open(p) as fh:
                body = fh.read()
                head = "\n".join(body.splitlines()[:15])
                h1 = DECL_H1.search(head)
                bold = DECL_BOLD.search(head)
                declared = (h1.group(1) if h1 else None) or (bold.group(1) if bold else None)
                if declared and declared.upper() not in id_set:
                    defects.append(
                        f"ORPHAN FILING: {relpath} declares itself {declared.upper()} "
                        f"but no registry entry exists")
                for lineno, line in enumerate(body.splitlines(), 1):
                    # A citation may end a sentence — "see GOV-77." — so the
                    # number stops at the last digit. Swallowing the period
                    # made every end-of-sentence reference invisible.
                    for m in re.finditer(r'\b(GOV|RND|ECO|REG|WBI|AUD)-(\d+(?:\.\d+)*)', line):
                        tok = m.group(0)
                        # retired numbers are historical: legal only inside the
                        # documents that record the renumbering
                        if tok in retired_ids:
                            if relpath not in retired_ids[tok].get("used_in", []):
                                defects.append(
                                    f"STALE RETIRED REF: {relpath}:{lineno} uses retired "
                                    f"{tok} ({retired_ids[tok]['reason']}) — outside its "
                                    f"historical docs")
                            continue
                        if resolves(tok):
                            continue
                        # RND-0 → RND-0.1 (prefix of a real filing)
                        if any(real.startswith(tok) for real in id_set):
                            continue
                        defects.append(
                            f"PHANTOM REF: {relpath}:{lineno} mentions {tok} "
                            f"(not in registry)")
    return defects

# ────────────────────────────────────────────────────────────── seal ──
def seal_path():
    return os.path.join(REG, "seal.json")


def seal_log_path():
    return os.path.join(REG, "seal-history.jsonl")


def sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_seal():
    p = seal_path()
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return None


def seal_corpus(reason=""):
    """Seal every registered document: a keyless, append-only record.

    The seal answers one question the registry alone cannot: *is the
    document I registered still the document on disk?* Each entry is the
    SHA-256 of a filing's own file. The root hashes the sorted entries,
    and each seal chains to the previous root (the PennyChain pattern,
    RND-3). No keys, no signatures — only hashes and history.

    Reseal on purpose after an intended edit. `govgen audit` reports
    SEAL DRIFT for any document that changed without a reseal.
    """
    import datetime
    filings = get_filings()
    entries = []
    for f in filings:
        if not f.get("file"):
            continue  # log-recorded filings live inside the log, not their own file
        p = os.path.join(BASE, f["file"]) if f["file"].startswith(f["repo"] + "/") \
            else os.path.join(repo_path(f["repo"]), f["file"])
        if not os.path.exists(p):
            continue
        entries.append({"id": f["id"], "file": os.path.relpath(p, BASE),
                        "sha256": sha256(p)})
    entries.sort(key=lambda e: e["file"])
    registry_hashes = {name: sha256(os.path.join(REG, name))
                       for name in ("filings.json", "tools.json", "divisions.json")
                       if os.path.exists(os.path.join(REG, name))}
    root_src = "\n".join(f"{e['file']}:{e['sha256']}" for e in entries)
    root_src += "\n" + "\n".join(f"{k}:{v}" for k, v in sorted(registry_hashes.items()))
    import hashlib
    root = hashlib.sha256(root_src.encode()).hexdigest()

    prev = None
    log = seal_log_path()
    if os.path.exists(log):
        with open(log) as f:
            lines = [ln for ln in f.read().splitlines() if ln.strip()]
        if lines:
            prev = json.loads(lines[-1])["root"]
    rec = {"schema": "wubu-corpus-seal-v1",
           "sealed": datetime.date.today().isoformat(),
           "documents": len(entries), "root": root, "prev_root": prev,
           "reason": reason or "routine seal",
           "entries": entries, "registry": registry_hashes}
    with open(seal_path(), "w") as f:
        json.dump(rec, f, indent=2)
    with open(log, "a") as f:
        f.write(json.dumps({k: rec[k] for k in
                            ("schema", "sealed", "documents", "root", "prev_root", "reason")}) + "\n")
    print(f"sealed {len(entries)} documents · root {root[:16]}… · prev {(prev or 'genesis')[:16]}…")
    if prev:
        chain = open(log).read().splitlines()
        last = json.loads(chain[-2])
        ok = last["root"] == prev
        print(f"chain: {'OK' if ok else 'BROKEN'} (seal #{len(chain)})")
    return rec


def verify_seal():
    """Recompute the seal from disk and compare with the recorded one."""
    seal = load_seal()
    if not seal:
        print("no seal recorded — run `govgen seal`")
        return 1
    bad = 0
    for e in seal["entries"]:
        p = os.path.join(BASE, e["file"])
        if not os.path.exists(p):
            print(f"  ✗ GONE  {e['file']}")
            bad += 1
        elif sha256(p) != e["sha256"]:
            print(f"  ✗ DRIFT {e['file']} ({e['id']})")
            bad += 1
    print(f"seal verify: {len(seal['entries']) - bad}/{len(seal['entries'])} "
          f"documents match · root {seal['root'][:16]}…")
    return 0 if bad == 0 else 1


# ─────────────────────────────────────────────────────────────── index ──
def gen_index():
    """Regenerate per-repo doc tables + master INDEX.md from registry."""
    filings = get_filings()
    tools = get_tools()
    divisions = get_divisions()

    # per-repo tables
    per_repo = {}
    for f in filings:
        per_repo.setdefault(f["repo"], []).append(f)

    for repo, rows in sorted(per_repo.items()):
        rows.sort(key=lambda r: (r["id"].split("-")[0], int(re.split(r'\D+', r["id"])[1] or 0)))
        table = ["| Filing | File | Title | Tools | Status |",
                 "|--------|------|-------|-------|--------|"]
        for r in rows:
            amd = f" *(amended by {', '.join(r['amended_by'])})*" if r.get("amended_by") else ""
            tools_ = ", ".join(f"`{t}`" for t in r["tools"]) if r["tools"] else "—"
            where = f"`{r['file']}`" if r.get("file") else f"*{r.get('record') or r.get('evidence')}*"
            table.append(f"| {r['id']} | {where} | {r['title']}{amd} | {tools_} | {r['status']} |")
        out = os.path.join(repo_path(repo), "INDEX.md")
        with open(out, "w") as f:
            f.write(f"# INDEX — {repo}\n\n")
            f.write("> **Generated by `govgen.py index` from `registry/filings.json`. "
                    "Do not hand-edit this file — edit the registry and regenerate.**\n\n")
            f.write(f"{len(rows)} filings.\n\n")
            f.write("\n".join(table) + "\n")
        print(f"  wrote {out} ({len(rows)} filings)")

    # master index
    master = ["# WuBu Government — Master Index",
              "",
              "> **Generated by `govgen.py index` from `registry/filings.json`.**",
              "",
              f"**{len(filings)} filings. {len(divisions['organs'])} organs. "
              f"One rule: every doctrine ships a tool.**",
              "",
              "## Organs",
              "",
              "| Organ | Repo | Division | Role |",
              "|-------|------|----------|------|"]
    for o in divisions["organs"]:
        master.append(f"| {o['name']} | `{o['repo']}` | {o['division']} | {o['role']} |")
    master += ["", "## Filings by division", ""]
    by_div = {}
    for f in filings:
        div = f["id"].split("-")[0]
        by_div.setdefault(div, []).append(f)
    for div in sorted(by_div):
        rows = sorted(by_div[div], key=lambda r: int(re.split(r'\D+', r["id"])[1] or 0))
        master.append(f"### {div} ({len(rows)})")
        master.append("")
        for r in rows:
            amd = f" *(amended by {', '.join(r['amended_by'])})*" if r.get("amended_by") else ""
            where = r.get('file') or r.get('record') or r.get('evidence') or '—'
            if where.startswith(r['repo'] + '/'):
                where = where
            else:
                where = f"{r['repo']}/{where}"
            master.append(f"- **{r['id']}** — {r['title']}{amd} — `{where}`")
        master.append("")
    master.append("## Tools")
    master.append("")
    master.append("| Tool | Python oracle | C11 module | CLI | Test | Filing |")
    master.append("|------|---------------|------------|-----|------|--------|")
    for t in sorted(tools, key=lambda x: x["name"]):
        master.append(f"| `{t['name']}` | {t['python'] or '—'} | `{t['c11']}` | "
                      f"`{t['cli'] or '—'}` | `{t['test'] or '—'}` | {t['filing']} |")
    master.append("")
    master.append("---")
    master.append("")
    master.append("*Generated. Filed. Done. Next.*")
    with open(os.path.join(BASE, "INDEX.md"), "w") as f:
        f.write("\n".join(master) + "\n")
    print(f"  wrote {os.path.join(BASE, 'INDEX.md')}")

# ──────────────────────────────────────────────────────────────── map ──
def gen_map():
    """Regenerate the society map section from the registry."""
    filings = get_filings()
    divisions = get_divisions()

    institutions = [f for f in filings if f["id"].startswith("GOV-12")]
    # The institutions are GOV-12..GOV-17 per filing order
    inst = {f["id"]: f for f in filings if f["id"] in
            [f"GOV-{n}" for n in range(12, 18)]}

    lines = ["## The institutions (generated from the registry)",
             "",
             "> **Generated by `govgen.py map`. The six institutions of the",
             "> society map are the GOV-12..GOV-17 filings.**",
             "",
             "| Filing | Institution | File | Title |",
             "|--------|-------------|------|-------|"]
    order = ["GOV-12", "GOV-13", "GOV-14", "GOV-15", "GOV-16", "GOV-17"]
    names = {
        "GOV-12": "The Dispatch", "GOV-13": "The Treaty", "GOV-14": "The Mint",
        "GOV-15": "The Ship", "GOV-16": "The Archive", "GOV-17": "The Vote",
    }
    for fid in order:
        f = inst.get(fid)
        if f:
            lines.append(f"| {fid} | **{names[fid]}** | `{f['file']}` | {f['title']} |")
    lines.append("")
    lines.append(f"Registry: `registry/filings.json` · Generated: `govgen.py map`")
    return "\n".join(lines)

# ─────────────────────────────────────────────────────────────── stats ──
def stats():
    filings = get_filings()
    tools = get_tools()
    divisions = get_divisions()["organs"]
    by_div = {}
    for f in filings:
        by_div.setdefault(f["id"].split("-")[0], 0)
        by_div[f["id"].split("-")[0]] += 1
    print("Filing counts by division:")
    for div, n in sorted(by_div.items()):
        print(f"  {div:5s} {n}")
    print(f"  TOTAL {len(filings)}")
    print(f"Tools: {len(tools)} (C11 modules: {sum(1 for t in tools if t['c11'])}, "
          f"CLIs: {sum(1 for t in tools if t['cli'])}, tests: {sum(1 for t in tools if t['test'])}, "
          f"Python oracles: {sum(1 for t in tools if t['python'])})")
    print(f"Organs: {len(divisions)}")
    with_tools = sum(1 for f in filings if f.get("tools"))
    print(f"Doctrines shipping ≥1 tool: {with_tools}/{len(filings)}")

# ─────────────────────────────────────────────────────────────── lang ──
def lang_report():
    """Run the space's own language gates over the whole corpus.

    plain_lang (RND-20 FRES gate) + plain_lang --ste (RND-22 STE gate)
    + zh_lang (GOV-10 Chinese gate). Produces a verdict table and
    writes CORPUS-LANG.md. The doctrine (RND-22) says: the standard
    applies to new + amended filings; pre-RND-22 filings may read
    REWRITE. The report is the machine's own audit of its prose.
    """
    import subprocess
    PLAIN = os.path.join(repo_path("wubucore"), "bin", "plain_lang")
    ZH = os.path.join(repo_path("wubucore"), "bin", "zh_lang")

    docs = []
    for root, dirs, files in os.walk(BASE):
        dirs[:] = [d for d in dirs if d not in ('.git', 'bin', 'src', 'apps',
                                                'tools', 'keys', 'registry',
                                                '.github', 'ledger')]
        for fn in files:
            if fn.endswith('.md') and fn != 'INDEX.md':
                docs.append(os.path.join(root, fn))

    rows = []
    n_clear = n_ste = n_zh = 0
    for d in sorted(docs):
        rel = os.path.relpath(d, BASE)
        # FRES gate
        try:
            r = subprocess.run([PLAIN, d], capture_output=True, text=True, timeout=10)
            out = r.stdout
            fres_verdict = "CLEAR" if "CLEAR" in out and "no rewrite" in out else "REWRITE"
        except Exception:
            fres_verdict = "ERR"
        # STE gate
        try:
            r = subprocess.run([PLAIN, "--ste", d], capture_output=True, text=True, timeout=10)
            ste = "STE CLEAR" if "STE CLEAR" in r.stdout else "STE REWRITE"
        except Exception:
            ste = "ERR"
        # zh gate: only meaningful if file has CJK
        zh = "—"
        try:
            with open(d, encoding='utf-8') as f:
                if any('\u4e00' <= ch <= '\u9fff' for ch in f.read()):
                    r = subprocess.run([ZH, d], capture_output=True, text=True, timeout=10)
                    zh = "ZH CLEAR" if "CLEAR" in r.stdout else "ZH REWRITE"
        except Exception:
            zh = "ERR"
        if fres_verdict == "CLEAR": n_clear += 1
        if ste == "STE CLEAR": n_ste += 1
        rows.append((rel, fres_verdict, ste, zh))

    lines = ["# Corpus Language Report",
             "",
             "> **Generated by `govgen.py lang` — the Hands run the space's",
             "> own language gates over every filing.**",
             "",
             f"**{len(rows)} docs scanned. FRES CLEAR: {n_clear}. "
             f"STE CLEAR: {n_ste}. Chinese-gated: {n_zh}.**",
             "",
             "The RND-22 doctrine: the standard applies to **new + amended**",
             "filings; pre-RND-22 filings may read REWRITE (written to FRES",
             "only). New filings must be CLEAR on both gates.",
             "",
             "| Doc | FRES (RND-20) | STE (RND-22) | zh (GOV-10) |",
             "|-----|---------------|--------------|-------------|"]
    for rel, f, s, z in rows:
        lines.append(f"| `{rel}` | {f} | {s} | {z} |")
    lines += ["", "*Generated. Filed. Done. Next.*"]
    out = os.path.join(BASE, "CORPUS-LANG.md")
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {out}: {n_clear}/{len(rows)} FRES CLEAR, "
          f"{n_ste}/{len(rows)} STE CLEAR")
    return rows

# ─────────────────────────────────────────────────────────────── main ──
def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "audit"
    as_json = "--json" in args
    if cmd == "audit":
        defects = audit()
        if as_json:
            import json as j
            print(j.dumps({"clean": len(defects) == 0, "defects": defects,
                           "count": len(defects)}))
            sys.exit(0 if not defects else 1)
        if defects:
            print(f"govgen: {len(defects)} defect(s) found:\n")
            for d in defects:
                print(f"  ✗ {d}")
            sys.exit(1)
        print("govgen: registry clean — every filing, tool, and reference resolves.")
        sys.exit(0)
    elif cmd == "seal":
        reason = " ".join(a for a in args[1:] if not a.startswith("--"))
        seal_corpus(reason)
    elif cmd == "verify-seal":
        sys.exit(verify_seal())
    elif cmd == "index":
        gen_index()
        print("govgen: indexes regenerated.")
    elif cmd == "map":
        print(gen_map())
    elif cmd == "lang":
        lang_report()
    elif cmd == "stats":
        if as_json:
            import json as j
            filings = get_filings()
            tools = get_tools()
            by_div = {}
            for f in filings:
                by_div.setdefault(f["id"].split("-")[0], 0)
                by_div[f["id"].split("-")[0]] += 1
            print(j.dumps({"filings": len(filings), "by_division": by_div,
                           "tools": len(tools),
                           "organs": len(get_divisions()["organs"]),
                           "doctrines_with_tools": sum(1 for f in filings if f.get("tools"))}))
        else:
            stats()
    elif cmd == "check":
        defects = audit()
        if defects:
            for d in defects:
                print(f"  ✗ {d}")
            sys.exit(1)
        print("govgen audit: CLEAN")
        # the gate is itself gated: prove the audit can still fail
        r = subprocess.run([sys.executable,
                            os.path.join(BASE, "tools", "test_govgen.py")],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stdout[-1500:])
            print("govgen check: GATE TESTS FAILED")
            sys.exit(1)
        print(r.stdout.strip().splitlines()[-1])
        r = subprocess.run(["make", "test"], cwd=repo_path("wubucore"),
                           capture_output=True, text=True)
        print(r.stdout[-800:])
        if r.returncode != 0:
            print("govgen check: WuBuCore tests FAILED")
            sys.exit(1)
        print("govgen check: ALL PASS")
    else:
        print(__doc__)
        sys.exit(2)

if __name__ == "__main__":
    main()
