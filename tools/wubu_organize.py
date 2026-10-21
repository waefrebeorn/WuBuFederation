#!/usr/bin/env python3
"""
wubu_organize.py — THE CORPUS ORGANIZER: the home AGI's filing
system for the research corpus.

The timeline aggregates; the corpus organizes. This tool reads
every civilization/event/gap in the timeline data and files it
into the research-corpus structure (by region, then era), so the
home AGI (llama-server) can read the corpus in organized order
and file summaries. It is the bridge between the scouter
(intake) and the AGI (organization).

Structure produced:
  research/africa/kush-nubia.md        <- one file per civilization
  research/mesoamerica/teotihuacan.md
  ...
Each file carries: verified span, source, key events, gap
candidates, and a hop-map stub (the Kevin Bacon path the home
AGI will complete).

Usage:
  python3 wubu_organize.py          # write the corpus files
  python3 wubu_organize.py --tree   # print the corpus tree
"""
import json
import os
import sys

BASE = "/home/wubu/copy_government"
HISTORY = os.path.join(BASE, "registry", "history", "history.json")
EVENTS = os.path.join(BASE, "registry", "history", "events.json")
CORPUS = os.path.join(BASE, "registry", "history", "corpus.json")
OUT = os.path.join(BASE, "research")

REGION_DIR = {
    "Africa": "africa", "East Africa": "africa", "Northeast Africa": "africa",
    "Southern Africa": "africa", "North Africa / Mediterranean": "africa",
    "West Africa": "africa", "Nile": "africa",
    "Mesoamerica": "mesoamerica", "Andes": "andes",
    "China": "china", "India": "india", "South India": "india",
    "Mesopotamia": "mesopotamia", "Iran": "iran",
    "Mediterranean": "mediterranean", "East Mediterranean": "mediterranean",
    "Italy": "mediterranean", "Aegean": "mediterranean",
    "Southeast Asia": "seasia", "Japan": "eastasia", "Korea": "eastasia",
    "Eurasia": "eurasia", "Central Asia": "eurasia",
    "Oceania": "oceania", "North America": "northamerica",
    "Scandinavia / North Atlantic": "north",
    "Eastern Europe": "north", "Global": "global",
}


def year_str(y):
    if y < 0:
        return f"{-y} BCE"
    return f"{y} CE" if y > 0 else "1 CE"


def region_dir(region):
    return REGION_DIR.get(region, "misc")


def slugify(name):
    return name.lower().replace(" ", "-").replace("(", "").replace(")", "")


def build():
    h = json.load(open(HISTORY))
    ev = json.load(open(EVENTS))
    corpus = json.load(open(CORPUS))
    civs = h["civilizations"]
    events = h["events"]
    gaps = ev["events"]

    os.makedirs(OUT, exist_ok=True)
    written = 0
    for c in sorted(civs, key=lambda x: x["start"]):
        rd = region_dir(c.get("region", "?"))
        d = os.path.join(OUT, rd)
        os.makedirs(d, exist_ok=True)
        name = c["name"]
        path = os.path.join(d, slugify(name) + ".md")
        rel_events = [e for e in events
                      if c["start"] <= e["year"] <= c["end"] + 150]
        # gap events mentioning this civ
        rel_gaps = [g for g in gaps if name.split(" ")[0].lower()
                    in g["name"].lower() or
                    name.split(" ")[0].lower() in g["claim"].lower()]
        lines = [
            f"# {name}",
            "",
            f"- **Region:** {c.get('region', '?')}",
            f"- **Span:** {year_str(c['start'])} to {year_str(c['end'])}",
            f"- **Source:** {c.get('source', '?')}",
            "",
            "## Key events",
            "",
        ]
        if rel_events:
            for e in sorted(rel_events, key=lambda x: x["year"]):
                lines.append(f"- **{year_str(e['year'])}:** {e['what']}")
        else:
            lines.append("- (no dated events filed yet — the home AGI "
                         "should research these)")
        lines.append("")
        lines.append("## Gap-event candidates")
        lines.append("")
        if rel_gaps:
            for g in rel_gaps:
                lines.append(f"- **{g['id']} ({g['type']}):** {g['name']}")
        else:
            lines.append("- none filed yet — the scouter should hunt for "
                         "isolated records and unacknowledged deaths here")
        lines.append("")
        lines.append("## Hop map (Kevin Bacon path — home AGI completes)")
        lines.append("")
        lines.append("1. claim → ?")
        lines.append("2. source → ?")
        lines.append("3. cross-check → ?")
        lines.append("")
        with open(path, "w") as f:
            f.write("\n".join(lines))
        written += 1

    # write the corpus index
    index = os.path.join(OUT, "CORPUS-INDEX.md")
    with open(index, "w") as f:
        f.write("# THE RESEARCH CORPUS — Index\n\n")
        f.write(f"**{len(civs)} civilizations, {len(events)} events, "
                f"{len(gaps)} gap events, filed by region.**\n\n")
        f.write("Wikipedia is the searchable system (articles by topic). "
                "The timeline is the aggregating system (everything dated). "
                "The corpus is the intake system (sources, filed by the "
                "home AGI).\n\n")
        by_region = {}
        for c in civs:
            rd = region_dir(c.get("region", "?"))
            by_region.setdefault(rd, []).append(c)
        for rd in sorted(by_region):
            f.write(f"## {rd}\n\n")
            for c in sorted(by_region[rd], key=lambda x: x["start"]):
                f.write(f"- **{c['name']}** ({year_str(c['start'])} – "
                        f"{year_str(c['end'])})\n")
            f.write("\n")
    print(f"wrote {written} civilization files + CORPUS-INDEX.md "
          f"under {OUT}")
    return written


def tree():
    for root, dirs, files in os.walk(OUT):
        level = root.replace(OUT, "").count(os.sep)
        indent = "  " * level
        print(f"{indent}{os.path.basename(root)}/")
        for f in sorted(files):
            print(f"{indent}  {f}")


if __name__ == "__main__":
    if "--tree" in sys.argv:
        tree()
    else:
        build()
