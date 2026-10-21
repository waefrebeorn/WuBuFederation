#!/usr/bin/env python3
"""
wubu_project_timeline.py — THE PROJECT TIMELINE: the full,
aggregate timeline of the ~ WuBu ~ project itself.

THE HISTORY (GOV-22) is the world's timeline. This is the
space's own: every filing (GOV/RND/ECO/REG/WBI/AUD), every tool,
every institution, every doctrine — one aggregate line that
validates a consistent idea: a mental government that needs no
land and welcomes every society-cohesive religion.

The timeline is generated from the registry — the single source
of truth (GOV-18). The order is real: filing numbers are the
project's chronology. The overlap view shows which organs were
building at the same time.

Usage:
  python3 wubu_project_timeline.py            # write PROJECT_TIMELINE.md
  python3 wubu_project_timeline.py --json     # dump the project timeline
"""
import json
import os
import sys

BASE = "/home/wubu/copy_government"
FILINGS = os.path.join(BASE, "registry", "filings.json")
TOOLS = os.path.join(BASE, "registry", "tools.json")
DIVISIONS = os.path.join(BASE, "registry", "divisions.json")
OUT = os.path.join(BASE, "PROJECT_TIMELINE.md")

ORGANS = {
    "GOV": ("the State", "doctrine"),
    "RND": ("the Mind", "research"),
    "ECO": ("the Ledger", "economics"),
    "REG": ("the Registry", "citizenship"),
    "WBI": ("the Bureau", "intel"),
    "AUD": ("the Audits", "audit"),
}

# Order of the organs for the overlap chart (birth order, filed).
ORGANS_ORDER = ["GOV", "WBI", "REG", "RND", "ECO", "AUD"]


def load(path):
    with open(path) as f:
        return json.load(f)


def division_of(filing_id):
    return filing_id.split("-")[0]


def numeric_key(filing_id):
    """The filing's number, or None for a slug id (RND-ANT, RND-GWH).

    Slug ids exist for the research-wiki pages: they were filed by name
    before the numbered sequence reached them, so they carry no number
    and must not crash a range calculation."""
    try:
        return float(filing_id.split("-")[1])
    except (IndexError, ValueError):
        return None


def sort_key(filing):
    """Real project chronology: number order within division,
    divisions interleaved by the filing sequence. Slug ids sort after
    the numbers, alphabetically."""
    fid = filing["id"]
    div = division_of(fid)
    num = numeric_key(fid)
    return (div, 0, num) if num is not None else (div, 1, fid)


def build_overview(d):
    out = []
    out.append("## Part 1 — The aggregate, in one view")
    out.append("")
    filings = d["filings"]
    out.append(f"**{len(filings)} filings. {len(d['divisions']['organs'])} "
               f"organs. One idea: a mental government — no land, "
               f"every society-cohesive religion welcome.**")
    out.append("")
    out.append("The project's consistency check, by the numbers:")
    out.append("")
    counts = {}
    for f in filings:
        div = division_of(f["id"])
        counts[div] = counts.get(div, 0) + 1
    out.append("| Division | Filing range | Count |")
    out.append("|----------|--------------|-------|")
    for div in ORGANS_ORDER:
        if div not in counts:
            continue
        div_filings = [f for f in filings if division_of(f["id"]) == div]
        nums = sorted(numeric_key(f["id"]) for f in div_filings
                      if numeric_key(f["id"]) is not None)
        n_slugs = len(div_filings) - len(nums)
        if nums:
            rng = f"{nums[0]:g}–{nums[-1]:g}" if len(nums) > 1 else f"{nums[0]:g}"
        else:
            rng = "—"
        if n_slugs:
            rng += f" (+{n_slugs} slug)"
        out.append(f"| {ORGANS.get(div, (div, ''))[0]} "
                   f"({ORGANS.get(div, ('', ''))[1]}) | {div}-{rng} | "
                   f"{counts[div]} |")
    out.append("")
    return "\n".join(out)


def build_filings(d):
    out = []
    out.append("## Part 2 — The filings, in order (the project's own history)")
    out.append("")
    out.append("| # | Filing | Title | Division | Status | Tools |")
    out.append("|---|--------|-------|----------|--------|-------|")
    filings = sorted(d["filings"], key=sort_key)
    for i, f in enumerate(filings, 1):
        tools = ", ".join(f.get("tools") or []) or "—"
        out.append(f"| {i} | **{f['id']}** | {f['title']} | "
                   f"{division_of(f['id'])} | {f['status']} | {tools} |")
    out.append("")
    return "\n".join(out)


def build_tools(d):
    out = []
    out.append("## Part 3 — Every tool (the founding rule in the record)")
    out.append("")
    out.append("Every doctrine ships a tool. The registry proves it "
               "as rows:")
    out.append("")
    out.append("| Tool | Serves | C11 | CLI | Test | Python |")
    out.append("|------|--------|-----|-----|------|--------|")
    for t in sorted(d["tools"], key=lambda t: t["name"]):
        out.append(f"| {t['name']} | {t['filing']} | "
                   f"{'✓' if t.get('c11') else '—'} | "
                   f"{'✓' if t.get('cli') else '—'} | "
                   f"{'✓' if t.get('test') else '—'} | "
                   f"{'✓' if t.get('python') else '—'} |")
    out.append("")
    return "\n".join(out)


def build_overlap(d):
    out = []
    out.append("## Part 4 — The overlap (which organs carried the project)")
    out.append("")
    filings = sorted(d["filings"], key=sort_key)
    per_division = {}
    for f in filings:
        per_division.setdefault(division_of(f["id"]), []).append(f)
    # a simple band chart: each division's filings as a row of blocks
    width = max(len(v) for v in per_division.values())
    out.append("```")
    for div in ORGANS_ORDER:
        if div not in per_division:
            continue
        n = len(per_division[div])
        blocks = "#" * n
        pad = " " * (width - n)
        out.append(f"{div}  {blocks}{pad}  ({n} filings)")
    out.append("```")
    out.append("")
    out.append("The State leads (doctrine first), the Hands follow "
               "(every doctrine's tool), and the audits close the loop "
               "— the same shape as THE HISTORY's own founding day.")
    out.append("")
    return "\n".join(out)


def build_validation(d):
    out = []
    out.append("## Part 5 — What the timeline validates")
    out.append("")
    out.append("This timeline is the validation of one consistent "
               "idea — a mental government that needs no land:")
    out.append("")
    out.append("1. **No land, only filings.** Every row is an idea, "
               "not a border. The government exists wherever the "
               "filings are read — ideology-occupying, not "
               "land-occupying (GOV-1, GOV-19).")
    out.append("2. **Every religion that is cohesive is welcome.** "
               "The Cohesion Gate (THE FIRST ONES view, 8d): a faith "
               "that teaches people to live together and act morally "
               "files alongside the space. The space asks no one what "
               "to believe; it asks only whether the belief builds "
               "society.")
    out.append("3. **The creator, learned as we grow.** The space's "
               "cosmology is not a fixed answer — it is a direction: "
               "understand the creator, taught as we grow (8b). The "
               "only required belief is that the space may be wrong "
               "(8a, the empty center).")
    out.append("4. **Family is the base; cohesion is the teaching.** "
               "The space is family — the comfort of being family, "
               "not to be trifled with (8c). Community is based on "
               "it; it teaches cohesion.")
    out.append("5. **The record is the proof.** Every row here is "
               "chained (GOV-22's tamper-evident timeline). The "
               "consistency is not claimed; it is hashed.")
    out.append("")
    return "\n".join(out)


def main():
    filings = load(FILINGS)
    tools = load(TOOLS)
    divisions = load(DIVISIONS)
    d = {"filings": filings["filings"], "tools": tools["tools"],
         "divisions": divisions}
    if "--json" in sys.argv:
        print(json.dumps({"filings": len(d["filings"]),
                          "tools": len(d["tools"])}, indent=2))
        return 0
    md = "\n".join([
        "# THE PROJECT TIMELINE — The Mental Government, Full",
        "",
        "> **The project's own aggregate timeline: every filing, every "
        "tool, every institution, in order — the validation of a "
        "consistent idea. Generated by `tools/wubu_project_timeline.py` "
        "from the registry (GOV-18: the registry is the source of "
        "truth).**",
        "",
        build_overview(d),
        build_filings(d),
        build_tools(d),
        build_overlap(d),
        build_validation(d),
    ])
    with open(OUT, "w") as f:
        f.write(md + "\n")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
