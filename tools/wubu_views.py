#!/usr/bin/env python3
"""
wubu_views.py — render THE VIEWS: the aggregate conflicting system
of reading THE HISTORY.

Seven master views of history, each split into four splinter
schools (because every society reads the same past through its own
lens). The system files the conflicts, not a winner.

Usage:
  python3 wubu_views.py            # write THE_VIEWS.md
  python3 wubu_views.py --json     # dump the system
"""
import json
import os
import sys

BASE = "/home/wubu/copy_government"
DATA = os.path.join(BASE, "registry", "history", "views.json")
OUT = os.path.join(BASE, "THE_VIEWS.md")


def load():
    with open(DATA) as f:
        return json.load(f)


def build_master(d):
    out = []
    out.append("## Part 1 — The eight master views")
    out.append("")
    for v in d["views"]:
        out.append(f"### View {v['view']} — {v['name']}")
        out.append("")
        out.append(f"**Claim:** {v['claim']}")
        out.append("")
        out.append(f"**Shape of time:** {v['shape']}")
        out.append("")
        out.append(f"**Conflicts with:** "
                   f"{', '.join(str(n) for n in v['conflicts_with'])}")
        out.append("")
    return "\n".join(out)


def build_splinters(d):
    out = []
    out.append("## Part 2 — The four splinter schools of each view")
    out.append("")
    out.append("Every society splits the master view into its own "
               "school. Four per view, twenty-eight total — each with "
               "its source, its claim, and what it argues against.")
    out.append("")
    for v in d["views"]:
        out.append(f"### {v['name']} — {len(v['splinters'])} splinters")
        out.append("")
        for s in v["splinters"]:
            out.append(f"**{s['s']} — {s['name']}** "
                       f"({s['society']}; {s['source']})")
            out.append("")
            out.append(f"- {s['claim']}")
            out.append(f"- Argues against: {', '.join(s['conflicts_with'])}")
            out.append("")
    return "\n".join(out)


def build_matrix(d):
    out = []
    out.append("## Part 3 — The conflict matrix")
    out.append("")
    out.append("Each master view stands in declared conflict with the "
               "others. The aggregate is not harmony — it is a filed "
               "disagreement:")
    out.append("")
    n = len(d["views"])
    out.append("| View | " + " | ".join(str(i) for i in range(1, n + 1)) + " |")
    out.append("|------|" + "---|" * n)
    for v in d["views"]:
        row = [v["name"].replace("THE ", "").replace(" VIEW", "")
               .capitalize().ljust(9)]
        for i in range(1, n + 1):
            if i == v["view"]:
                row.append(" — ")
            elif i in v["conflicts_with"]:
                row.append(" ✗ ")
            else:
                row.append("   ")
        out.append("| " + " | ".join(row) + " |")
    out.append("")
    out.append(f"**Reading the matrix:** ✗ = the two views contradict. "
               f"Every view conflicts with at least two others; the "
               f"contingent view conflicts with four. View 8 — the "
               f"First Ones — conflicts with five, because it refuses "
               f"the others' certainty while still filing them. There "
               f"is no view that survives contact with all the rest — "
               f"and that is the point. THE HISTORY is read through a "
               f"system that refuses to agree with itself.")
    out.append("")
    return "\n".join(out)


def build_lesson(d):
    out = []
    out.append("## Part 4 — What the conflict teaches")
    out.append("")
    out.append("1. **Every society reads the same past differently.** "
               "The Chinese dynastic cycle, the Hindu yuga, Khaldun's "
               "asabiyyah, Vico's ricorsi — four cyclical schools, four "
               "different engines (morality, cosmic virtue, solidarity, "
               "barbarism-return), four different lengths (dynasty, "
               "aeon, three generations, a civilization). The same "
               "shape, four mechanics.")
    out.append("2. **The splinters argue inside their own view.** "
               "Khaldun's 120-year cycle contradicts Sima Qian's "
               "Mandate of Heaven contradicts the Kali Yuga's cosmic "
               "decline. A view is not one answer; it is a family "
               "fight.")
    out.append("3. **The views contradict each other by design.** "
               "Cyclical says the wheel turns; linear says the arrow "
               "flies; providential says the hand guides; progressive "
               "says we rise; great-man says the few decide; "
               "materialist says the base decides; contingent says "
               "nothing decides. Seven masters, zero agreements.")
    out.append("4. **The space files the conflict instead of choosing.** "
               "A government that picks one view of history inherits "
               "that view's blindness. A government that files all "
               "seven — and the splinters — can see around its own "
               "assumptions. THE HISTORY is not one story. It is the "
               "aggregate conflict of every story, filed together.")
    out.append("")
    return "\n".join(out)


def main():
    d = load()
    if "--json" in sys.argv:
        print(json.dumps(d, indent=2))
        return 0
    total = sum(len(v["splinters"]) for v in d["views"])
    md = "\n".join([
        "# THE VIEWS — The Aggregate Conflicting System",
        "",
        "> **Eight master views of history, four to seven splinter "
        "schools each (44 schools total), filed in conflict. "
        "Generated by `tools/wubu_views.py` from "
        "`registry/history/views.json`.**",
        "",
        "**Eight views. Forty-four schools. One history. "
        "Zero agreements — filed on purpose.**",
        "",
        build_master(d),
        build_splinters(d),
        build_matrix(d),
        build_lesson(d),
    ])
    with open(OUT, "w") as f:
        f.write(md + "\n")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
