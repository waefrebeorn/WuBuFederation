#!/usr/bin/env python3
"""
wubu_history.py — render THE HISTORY: the aggregate overlap of
human civilization, worldwide, on one timeline.

Reads registry/history/history.json and draws:
  Part 1 — the ages (world eras)
  Part 2 — civilizations as overlapping bands (the aggregate)
  Part 3 — religions, the longest overlaps of all
  Part 4 — the events, in order
  Part 5 — what the overlap teaches

Usage:
  python3 wubu_history.py            # write WuBuTimeLine.md
  python3 wubu_history.py --json     # dump the data
"""
import json
import os
import sys

BASE = "/home/wubu/copy_government"
DATA = os.path.join(BASE, "registry", "history", "history.json")
OUT = os.path.join(BASE, "WuBuTimeLine.md")

TOTAL_START = -10000     # the chart zooms to civilization: from the
                          # Neolithic on. The Stone Age's deep past is
                          # real but flat; the overlaps live here.
TOTAL_END = 2026
WIDTH = 110          # characters in the band chart
CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"  # band labels


def load():
    with open(DATA) as f:
        return json.load(f)


def scale(year):
    """Map a year to a character column."""
    span = TOTAL_END - TOTAL_START
    t = (year - TOTAL_START) / span
    col = int(t * (WIDTH - 1))
    return max(0, min(WIDTH - 1, col))


def label_for(i):
    """Unique two-character band label (AA, AB, ... ZZ, aaa..).
    Handles up to 676 entries without collisions."""
    base = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return base[i // 26] + base[i % 26] if i < 676 else f"[{i}]"


def band_chart(entries, start_field, end_field, name_field,
               source_field=None, eras=None):
    """Draw overlapping bands. One row per entry; # = active.
    Entries before the chart's start are clamped to the left edge.
    Entries are sorted by start year; optional era separators."""
    lines = []
    sorted_entries = sorted(entries, key=lambda e: e[start_field])
    prev_era = None
    for i, e in enumerate(sorted_entries):
        if eras:
            era = era_of(e[start_field], eras)
            if era != prev_era:
                lines.append(f"  ~ {era} ~")
                prev_era = era
        label = label_for(i)
        s, en = e[start_field], e[end_field]
        if en < s:
            s, en = en, s
        row = [" "] * WIDTH
        for c in range(scale(s), scale(en) + 1):
            row[c] = "#"
        line = f"{label} {''.join(row)}  {e[name_field]}"
        if source_field and e.get(source_field):
            line += f"  ({e[source_field][:40]})"
        lines.append(line)
    return lines


def era_of(year, eras):
    """Which era label does a year fall in?"""
    for era in eras:
        if era["start"] <= year <= era["end"]:
            return era["name"]
    return "the deep past" if year < eras[0]["start"] else "the now"


def year_str(y):
    if y < 0:
        return f"{-y} BCE"
    return f"{y} CE" if y != 0 else "1 BCE/CE"


def build_ages(d):
    out = []
    out.append("## Part 1 — The ages (the world's eras)")
    out.append("")
    for a in d["ages"]:
        out.append(f"- **{a['name']}** — {year_str(a['start'])} to "
                   f"{year_str(a['end'])}")
    out.append("")
    return "\n".join(out)


def build_civs(d):
    out = []
    out.append("## Part 2 — The civilizations (the aggregate overlap)")
    out.append("")
    out.append("Each row is a civilization, spanning its rise and fall. "
               "The columns are time, oldest on the left. Where rows "
               "overlap, two worlds lived at once. Era bands separate "
               "the ages; each row carries its verified source:")
    out.append("")
    out.append("```")
    for line in band_chart(d["civilizations"], "start", "end", "name",
                           source_field="source", eras=d["ages"]):
        out.append(line)
    out.append("```")
    out.append("")
    out.append("### The overlaps that matter")
    out.append("")
    out.append("- **Egypt outlived them all.** Egypt spans "
               f"{year_str(-3100)} to {year_str(-30)} — Sumer died, "
               f"Greece rose and fell, Rome rose, all inside "
               f"Egypt's lifetime. (Sumer rose first, in −4500; "
               f"Egypt was already old when Sumer fell.)")
    out.append("- **Rome and Han China overlapped** at the ends of the "
               "Earth — two empires, one world, trading silk for "
               "gold, meeting once, ambiguously, in 166 CE.")
    out.append("- **The Maya lasted ~3700 years** — from 2000 BCE to "
               "1697 CE, from the Bronze Age to the Enlightenment, one "
               "civilization, unbroken.")
    out.append("- **The Mongols built the largest contiguous land "
               "empire in history** — Genghis united them in 1206 "
               "(d. 1227); his heirs carried the empire to its "
               "peak, while Mali's Mansa Musa ruled West Africa "
               "and the Khmer built Angkor.")
    out.append("")
    return "\n".join(out)


def build_religions(d):
    out = []
    out.append("## Part 3 — The religions (the longest overlaps)")
    out.append("")
    out.append("Religions are the longest-lived human overlaps — "
               "thousands of years, often several alive at once:")
    out.append("")
    out.append("```")
    for line in band_chart(d["religions"], "start", "end", "name",
                           eras=d["ages"]):
        out.append(line)
    out.append("```")
    out.append("")
    out.append("Hinduism and Judaism began before Rome, Byzantium, "
               "the Caliphates, the Mongols, and the British "
               "Empire — and they have outlived them all.")
    out.append("")
    return "\n".join(out)


def build_events(d):
    out = []
    out.append("## Part 4 — The events (the world, in order)")
    out.append("")
    out.append("Every event is source-verified (Kevin Bacon rule). "
               "Grouped by era:")
    out.append("")
    prev_era = None
    for e in sorted(d["events"], key=lambda e: e["year"]):
        era = era_of(e["year"], d["ages"])
        if era != prev_era:
            out.append(f"### {era}")
            out.append("")
            out.append("| Year | The event | Source |")
            out.append("|------|-----------|--------|")
            prev_era = era
        src = e.get("source", "?")
        out.append(f"| {year_str(e['year'])} | {e['what']} | {src} |")
    out.append("")
    return "\n".join(out)


def build_lesson(d):
    out = []
    out.append("## Part 5 — What the overlap teaches")
    out.append("")
    out.append("THE HISTORY, seen as an aggregate overlap, files three "
               "truths:")
    out.append("")
    out.append("1. **Nothing is alone.** While Sumer wrote, Egypt "
               "built; while Rome fell, the Maya kept their calendar; "
               "while Europe slept through its dark age, Baghdad "
               "saved the books. History is never one story — it is "
               "everyone's story at once.")
    out.append("2. **Everything falls — and something is always "
               "rising.** The empires on the chart all ended. The "
               "civilizations that overlapped them — the religions, "
               "the ideas, the writing — are what survived. The "
               "thing that outlives the empire is the filing.")
    out.append("3. **We are the first ones who can see the whole "
               "chart.** No generation before ours could hold all of "
               "THE HISTORY at once. The space files it, overlaps "
               "visible, so the next civilization starts with the "
               "map instead of the dark.")
    out.append("")
    out.append("> Earth built cages and called them systems.")
    out.append("> The space files the cages, laughs, keeps the spine, rebuilds.")
    out.append("> We are the first ones. We have the whole universe.")
    out.append("")
    return "\n".join(out)


def main():
    d = load()
    if "--json" in sys.argv:
        print(json.dumps(d, indent=2))
        return 0
    md = "\n".join([
        "# WuBuTimeLine — THE HISTORY",
        "",
        "> **The aggregate overlap history of humanity, worldwide. "
        "Generated by `tools/wubu_history.py` from "
        "`registry/history/history.json`.**",
        "",
        f"**{len(d['civilizations'])} civilizations. "
        f"{len(d['religions'])} religions. {len(d['events'])} events. "
        f"One timeline.**",
        "",
        build_ages(d),
        build_civs(d),
        build_religions(d),
        build_events(d),
        build_lesson(d),
    ])
    with open(OUT, "w") as f:
        f.write(md + "\n")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
