#!/usr/bin/env python3
"""
wubu_events.py — render THE GAP EVENTS: timeline events of overlap
or anomaly significance (GOV-27).

Three gap types, filed from the user's framing:
  ISOLATED-RECORD      — one society recording a world incident,
                         or a world silent on one society's record
  UNACKNOWLEDGED-DEATH — a society's end the world did not
                         acknowledge — or copied at its death
  OVERLAP-ANOMALY      — worlds alive together, never connected;
                         or one world event recorded by many,
                         connected only by modern science
  ORAL-HISTORY         — Homeric/oral tradition triangulated
                         against archaeology and written archives

The timeline's job is tracking: anthropology, archaeology, oral
history, the written record. These are the events where the
record itself is the anomaly.

Usage:
  python3 wubu_events.py            # write GAP_EVENTS.md
  python3 wubu_events.py --json     # dump the gap-event list
"""
import json
import os
import sys

BASE = "/home/wubu/copy_government"
EVENTS = os.path.join(BASE, "registry", "history", "events.json")
OUT = os.path.join(BASE, "GAP_EVENTS.md")

TYPES = {
    "ISOLATED-RECORD": ("isolated-record", "one society records a world incident, or the world stays silent on one society's record"),
    "UNACKNOWLEDGED-DEATH": ("unacknowledged-death", "a society's end the world did not acknowledge — or copied at its death"),
    "OVERLAP-ANOMALY": ("overlap-anomaly", "worlds alive together never connected; or one world event recorded by many, connected only by modern science"),
    "ORAL-HISTORY": ("oral-history", "Homeric/oral tradition triangulated against archaeology and the written archive"),
}


def load():
    with open(EVENTS) as f:
        return json.load(f)


def build_counts(d):
    out = []
    out.append("## Part 1 — The gap types, filed")
    out.append("")
    counts = {}
    for e in d["events"]:
        counts[e["type"]] = counts.get(e["type"], 0) + 1
    out.append(f"**{len(d['events'])} gap events filed.** The timeline "
               f"tracks what happened AND what the record did — or "
               f"failed to do — about it.")
    out.append("")
    out.append("| Gap type | Events | What it means |")
    out.append("|----------|--------|---------------|")
    for t, (short, meaning) in TYPES.items():
        out.append(f"| **{t}** | {counts.get(t, 0)} | {meaning} |")
    out.append("")
    return "\n".join(out)


def build_events(d):
    out = []
    out.append("## Part 2 — The events, in order")
    out.append("")
    for e in d["events"]:
        out.append(f"### {e['id']} — {e['name']} ({e['date']})")
        out.append("")
        out.append(f"**Type:** {e['type']}")
        out.append("")
        out.append(f"**The event:** {e['claim']}")
        out.append("")
        out.append(f"**The gap:** {e['gap']}")
        out.append("")
        out.append(f"**Sources:** {e['sources']}")
        out.append("")
        out.append(f"**Significance:** {e['significance']}")
        out.append("")
    return "\n".join(out)


def build_lesson(d):
    out = []
    out.append("## Part 3 — Why the government files the gaps")
    out.append("")
    out.append("A government that reads only the acknowledged events "
               "reads the world's own retelling of itself. The gaps "
               "are where the record lies:")
    out.append("")
    out.append("1. **Isolated records** teach which societies kept "
               "the attention infrastructure to notice. The Song "
               "Astronomical Bureau recorded a supernova Europe "
               "never saw — not because Europe's sky was different, "
               "but because its attention was.")
    out.append("2. **Unacknowledged deaths** teach that a society "
               "can vanish from the record and still matter — and "
               "that a world which copies a dying society's work "
               "without naming it has already lied once.")
    out.append("3. **Overlap anomalies** teach that worlds can "
               "trade, know each other, and still never meet face "
               "to face — and that one world event, recorded by "
               "four chronicles in four languages, can wait 1,400 "
               "years for science to connect the dots.")
    out.append("4. **Oral history** teaches the timeline's own "
               "method: Homer carried Troy for six centuries before "
               "anyone wrote it down. Memory can outlast the "
               "archive. The space files both.")
    out.append("")
    out.append("The ~ WuBu ~ timeline is a tracking project: "
               "anthropology, archaeology, Homeric oral history, "
               "the written record — filed side by side, because "
               "the gaps between them are where the truth hides.")
    out.append("")
    return "\n".join(out)


def main():
    d = load()
    if "--json" in sys.argv:
        print(json.dumps({"total": len(d["events"]),
                          "by_type": {t: sum(1 for e in d["events"]
                                             if e["type"] == t)
                                      for t in TYPES}},
                         indent=2))
        return 0
    md = "\n".join([
        "# THE GAP EVENTS — Overlap and Anomaly Significance",
        "",
        "> **Filed under GOV-27. The timeline's job is tracking — "
        "anthropology, archaeology, Homeric oral history, the "
        "written record. These are the events where the record "
        "itself is the anomaly. Generated by "
        "`tools/wubu_events.py` from `registry/history/events.json`.**",
        "",
        build_counts(d),
        build_events(d),
        build_lesson(d),
    ])
    with open(OUT, "w") as f:
        f.write(md + "\n")
    print(f"wrote {OUT} — {len(d['events'])} gap events")
    return 0


if __name__ == "__main__":
    sys.exit(main())
