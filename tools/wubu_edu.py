#!/usr/bin/env python3
"""
wubu_edu.py — EDUCATION EFFICACY: does the government teach?

The First Ones claim (GOV-25): "we are taught as we grow.
Teaching is the community's work." This tool measures it.

Every filing is scored on four rungs of teaching:
  1. TEACH    — the doctrine is readable (FRES CLEAR, RND-20)
  2. PRACTICE — the doctrine ships a real tool (GOV-10 law)
  3. PROOF    — the tool is verified (test or documented run)
  4. CHAIN    — the filing resolves in the registry (no phantom)

A filing that teaches is one where a newcomer can read the
doctrine, run its tool, watch it prove itself, and find it in
the map of the whole. A division's efficacy is the share of its
filings that climb all four rungs.

Usage:
  python3 wubu_edu.py            # write EDUCATION_EFFICACY.md
  python3 wubu_edu.py --json     # machine-readable scores
"""
import json
import os
import re
import subprocess
import sys

BASE = "/home/wubu/copy_government"
FILINGS = os.path.join(BASE, "registry", "filings.json")
TOOLS = os.path.join(BASE, "registry", "tools.json")
OUT = os.path.join(BASE, "EDUCATION_EFFICACY.md")
PLAIN_LANG = os.path.join(BASE, "wubucore", "bin", "plain_lang")

ORGANS = {
    "GOV": ("the State", "doctrine"),
    "WBI": ("the Bureau", "intel"),
    "RND": ("the Mind", "research"),
    "ECO": ("the Ledger", "economics"),
    "REG": ("the Registry", "citizenship"),
    "AUD": ("the Audits", "audit"),
}
ORGANS_ORDER = ["GOV", "WBI", "RND", "ECO", "REG", "AUD"]


def load(path):
    with open(path) as f:
        return json.load(f)


def div_of(fid):
    return fid.split("-")[0]


def fres_clear(filing):
    """TEACH rung: the doctrine's file passes the plain-English gate."""
    repo = filing["repo"]
    fpath = os.path.join(BASE, repo, filing["file"])
    if not os.path.exists(fpath):
        return False
    try:
        r = subprocess.run([PLAIN_LANG, fpath], capture_output=True,
                           text=True, timeout=30)
        return "CLEAR" in r.stdout and "NEEDS WORK" not in r.stdout
    except Exception:
        return False


def tool_verified(tool_name):
    """PROOF rung: the tool has a test file or a verified claim."""
    for t in load(TOOLS)["tools"]:
        if t["name"] == tool_name:
            if t.get("test"):
                return True
            if t.get("verified"):
                return True
    return False


def filing_tools(filing):
    names = [n for n in filing.get("tools") or [] if n]
    if not names:
        return []
    tools = {t["name"]: t for t in load(TOOLS)["tools"]}
    return [n for n in names if n in tools]


def score_filing(filing):
    teach = fres_clear(filing)
    tools = filing_tools(filing)
    practice = bool(tools) or filing["status"] != "filed"
    # a filing without a tool still teaches if it is a protocol/event
    # (e.g. Penny Day); PRACTICE means 'the doctrine reaches practice'
    proof = any(tool_verified(n) for n in tools)
    return {
        "id": filing["id"],
        "title": filing["title"][:60],
        "div": div_of(filing["id"]),
        "teach": teach,
        "practice": bool(tools),
        "proof": proof,
        "chain": True,  # filled below
        "tools": tools,
    }


def main():
    filings = [f for f in load(FILINGS)["filings"]
               if f["status"] == "filed"]
    scores = [score_filing(f) for f in filings]
    # CHAIN rung: verify by running the registry audit
    try:
        r = subprocess.run(["python3", os.path.join(BASE, "tools",
                                                    "govgen.py"), "audit"],
                           capture_output=True, text=True, timeout=60)
        chain_ok = "registry clean" in r.stdout
    except Exception:
        chain_ok = False
    for s in scores:
        s["chain"] = chain_ok

    # division aggregates
    divs = {}
    for s in scores:
        d = divs.setdefault(s["div"], {"n": 0, "all4": 0,
                                       "teach": 0, "practice": 0,
                                       "proof": 0, "chain": 0})
        d["n"] += 1
        for k in ("teach", "practice", "proof", "chain"):
            if s[k]:
                d[k] += 1
        if all(s[k] for k in ("teach", "practice", "proof", "chain")):
            d["all4"] += 1

    total = len(scores)
    all4 = sum(1 for s in scores
               if all(s[k] for k in ("teach", "practice", "proof",
                                     "chain")))
    pct = lambda a, b: f"{100.0 * a / b:.0f}%" if b else "—"

    lines = []
    lines.append("# EDUCATION EFFICACY — Does the government teach?")
    lines.append("")
    lines.append("> **Filed under GOV-26. The First Ones claim: "
                 "\"we are taught as we grow; teaching is the "
                 "community's work.\" This is the measure. Every "
                 "filing climbs four rungs — TEACH (readable, "
                 "RND-20), PRACTICE (ships a tool, GOV-10), PROOF "
                 "(tool verified), CHAIN (registry resolves). "
                 "Generated by `tools/wubu_edu.py`.**")
    lines.append("")
    lines.append("## Part 1 — The verdict")
    lines.append("")
    lines.append(f"**{all4}/{total} filings teach on all four rungs "
                 f"({pct(all4, total)}). Registry chain: "
                 f"{'VERIFIED' if chain_ok else 'BROKEN'}.**")
    lines.append("")
    lines.append("| Division | Filings | TEACH | PRACTICE | PROOF | "
                 "CHAIN | All four |")
    lines.append("|----------|---------|-------|----------|-------|"
                 "-------|----------|")
    for d in ORGANS_ORDER:
        if d not in divs:
            continue
        x = divs[d]
        lines.append(f"| {ORGANS.get(d, (d, ''))[0]} ({d}) | {x['n']} "
                     f"| {x['teach']} | {x['practice']} | {x['proof']} "
                     f"| {x['chain']} | {x['all4']} |")
    lines.append("")
    lines.append("## Part 2 — The filings that teach (all four rungs)")
    lines.append("")
    lines.append("| Filing | What it teaches | Proof |")
    lines.append("|--------|-----------------|-------|")
    for s in sorted(scores, key=lambda x: x["id"]):
        if all(s[k] for k in ("teach", "practice", "proof", "chain")):
            proof = ", ".join(s["tools"]) if s["tools"] else "chained"
            lines.append(f"| **{s['id']}** | {s['title']} | {proof} |")
    lines.append("")
    lines.append("## Part 3 — The gaps (teach without proof, or "
                 "practice without teach)")
    lines.append("")
    gaps = [s for s in scores if not all(s[k] for k in
                                         ("teach", "practice", "proof",
                                          "chain"))]
    if not gaps:
        lines.append("None — every filing teaches on all four rungs.")
    else:
        lines.append("| Filing | TEACH | PRACTICE | PROOF | CHAIN | "
                     "Missing |")
        lines.append("|--------|-------|----------|-------|-------|"
                     "---------|")
        for s in sorted(gaps, key=lambda x: x["id"]):
            miss = [k for k in ("teach", "practice", "proof", "chain")
                    if not s[k]]
            lines.append(f"| **{s['id']}** | {'✓' if s['teach'] else '✗'} "
                         f"| {'✓' if s['practice'] else '✗'} | "
                         f"{'✓' if s['proof'] else '✗'} | "
                         f"{'✓' if s['chain'] else '✗'} | "
                         f"{', '.join(miss)} |")
    lines.append("")
    lines.append("## Part 4 — The lesson")
    lines.append("")
    lines.append("Education efficacy is the government's own report "
                 "card. A doctrine that reads well but ships no tool "
                 "teaches words, not work. A tool with no proof "
                 "teaches confidence, not truth. The four rungs are "
                 "the stairs a newcomer climbs from reading to "
                 "doing — and the space's whole claim is that the "
                 "climb is the community's work.")
    lines.append("")
    lines.append(f"*EDU efficacy: {pct(all4, total)} of the "
                 f"government teaches on all four rungs. Filed. "
                 f"Done. Next.*")
    lines.append("")

    with open(OUT, "w") as f:
        f.write("\n".join(lines))
    print(f"wrote {OUT} — {all4}/{total} teach on all four rungs")

    if "--json" in sys.argv:
        print(json.dumps({"total": total, "all4": all4,
                          "divisions": {k: v for k, v in divs.items()}},
                         indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
