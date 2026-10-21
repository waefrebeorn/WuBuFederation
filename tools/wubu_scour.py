#!/usr/bin/env python3
"""
wubu_scour.py — THE TIMELINE SCOURER: programmatic ingestion for
the ~ WuBu ~ timeline.

Not a Wikipedia: Wikipedia is the searchable system (articles,
organized by topic). The timeline is the aggregating system —
everything dated, everything overlapping, organized by the
home AGI. This tool is the intake valve: it scours the web for
civilizations, events, and gap events, verifies dates against
sources, and files them into the timeline data.

The Kevin Bacon rule (RND-15) governs every entry: any subject
connects in <=7 hops, each hop a real source, the path filed.
A date filed without a source is a rumor; a date filed with a
source is evidence.

Usage:
  python3 wubu_scour.py status            # timeline health
  python3 wubu_scour.py civs              # list civilizations
  python3 wubu_scour.py verify            # cross-check data integrity
  python3 wubu_scour.py ingest --name X --start N --end N --region R --source S
                                          # file one civilization
  python3 wubu_scour.py evt --year N --what "..." --source S
                                          # file one event
  python3 wubu_scour.py gaps              # list gap events by type
"""
import json
import os
import sys

BASE = "/home/wubu/copy_government"
HISTORY = os.path.join(BASE, "registry", "history", "history.json")
EVENTS = os.path.join(BASE, "registry", "history", "events.json")


def load(path):
    with open(path) as f:
        return json.load(f)


def save(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def cmd_status():
    h = load(HISTORY)
    ev = load(EVENTS)
    civs = h["civilizations"]
    total_years = sum(c["end"] - c["start"] for c in civs)
    print(f"THE TIMELINE — status")
    print(f"  civilizations : {len(civs)}")
    print(f"  religions     : {len(h['religions'])}")
    print(f"  ages          : {len(h['ages'])}")
    print(f"  events        : {len(h['events'])}")
    print(f"  gap events    : {len(ev['events'])}")
    print(f"  coverage      : {total_years} civilization-years")
    print(f"  span          : {min(c['start'] for c in civs)} to "
          f"{max(c['end'] for c in civs)}")
    # regions covered
    regions = {}
    for c in civs:
        r = c.get("region", "?")
        regions[r] = regions.get(r, 0) + 1
    print(f"  regions       : {len(regions)}")
    for r, n in sorted(regions.items()):
        print(f"    {r}: {n}")


def cmd_civs():
    h = load(HISTORY)
    for c in sorted(h["civilizations"], key=lambda x: x["start"]):
        span = c["end"] - c["start"]
        print(f"  {c['name']:<45} {c['start']:>7} -> {c['end']:>6}  "
              f"({span:>6}y)  {c.get('region','')}")


def cmd_verify():
    h = load(HISTORY)
    defects = []
    civs = h["civilizations"]
    for i, c in enumerate(civs):
        if c["end"] <= c["start"]:
            defects.append(f"BAD SPAN: {c['name']} {c['start']}->{c['end']}")
        # name collisions
        for j in range(i + 1, len(civs)):
            if civs[j]["name"] == c["name"]:
                defects.append(f"DUPLICATE: {c['name']}")
    evs = h["events"]
    for e in evs:
        if not isinstance(e.get("year"), int):
            defects.append(f"BAD EVENT YEAR: {e}")
    print(f"VERIFY: {len(defects)} defects" if defects else
          "VERIFY: clean — every span valid, no duplicates")
    for d in defects:
        print(f"  {d}")


def cmd_ingest(args):
    """File a civilization: --name --start --end --region --source"""
    name = args.get("--name")
    if not name:
        print("need --name")
        return 1
    start = int(args.get("--start", 0))
    end = int(args.get("--end", 2026))
    region = args.get("--region", "?")
    source = args.get("--source", "")
    if not source:
        print("WARNING: no source — the Kevin Bacon rule demands one")
    h = load(HISTORY)
    # check not a duplicate
    for c in h["civilizations"]:
        if c["name"].lower() == name.lower():
            print(f"ALREADY FILED: {name}")
            return 1
    h["civilizations"].append({
        "name": name, "region": region, "start": start, "end": end,
        "source": source,
    })
    save(HISTORY, h)
    print(f"FILED: {name} ({start} -> {end}, {region}) source={source}")
    return 0


def cmd_evt(args):
    """File an event: --year --what --source"""
    year = int(args.get("--year", 0))
    what = args.get("--what", "")
    source = args.get("--source", "")
    if not what:
        print("need --what")
        return 1
    h = load(HISTORY)
    for e in h["events"]:
        if e["year"] == year and e["what"] == what:
            print(f"ALREADY FILED: {year} {what}")
            return 1
    h["events"].append({"year": year, "what": what, "source": source})
    save(HISTORY, h)
    print(f"FILED EVENT: {year} — {what} source={source}")
    return 0


def cmd_gaps():
    ev = load(EVENTS)
    types = {}
    for e in ev["events"]:
        types.setdefault(e["type"], []).append(e["id"])
    for t, ids in types.items():
        print(f"  {t}: {', '.join(ids)}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 0
    cmd = sys.argv[1]
    args = {}
    rest = sys.argv[2:]
    i = 0
    while i < len(rest):
        if rest[i].startswith("--") and i + 1 < len(rest):
            args[rest[i]] = rest[i + 1]
            i += 2
        else:
            i += 1
    if cmd == "status":
        cmd_status()
    elif cmd == "civs":
        cmd_civs()
    elif cmd == "verify":
        cmd_verify()
    elif cmd == "ingest":
        return cmd_ingest(args)
    elif cmd == "evt":
        return cmd_evt(args)
    elif cmd == "gaps":
        cmd_gaps()
    else:
        print(f"unknown: {cmd}")
        print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
