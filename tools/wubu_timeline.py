#!/usr/bin/env python3
"""
wubu_timeline.py — the WuBuTimeLine: the tamper-evident,
overlapping history chain of the ~ WuBu ~ space.

Every file in the space is hashed into a snapshot. Each snapshot
stores the full hash map and chains to the previous by root:

  root_N = SHA256(prev_root | sorted(rel|hash for every file))

The root is the overlap: every file's hash lives inside it.

Properties:
  - STOP MODIFICATION: edit any file — or any old snapshot in the
    ledger — and every later root breaks. The latest root is the
    published truth; a mismatch means someone changed something.
  - DISCOVER OLD MODIFICATIONS: diff any two snapshots and see
    exactly which files changed between them, and when. The chain
    keeps every state, so old modifications are found, not
    forgotten.
  - Append-only: a snapshot never edits a past snapshot; it only
    adds the next link.

Usage:
  wubu_timeline.py snapshot            # hash the corpus, append a link
  wubu_timeline.py verify              # current state vs latest link
  wubu_timeline.py history             # every snapshot + root
  wubu_timeline.py diff <N> <M>        # files changed between links
  wubu_timeline.py find <file>         # every change to one file
  wubu_timeline.py check               # full chain integrity
"""
import hashlib
import json
import os
import sys
from datetime import datetime

BASE = "/home/wubu/copy_government"
REPOS = ["wubugov", "wubucitizen", "wubuintel", "wuburesearch",
         "wubuecon", "wubucore"]
LEDGER = os.path.join(BASE, "registry", "timeline")
LEDGER_FILE = os.path.join(LEDGER, "chain.json")

# Files that are not history (generated artifacts, caches, metadata).
SKIP = ("__pycache__", ".git", ".pyc", ".o$", "bulk_fix.py",
        "scan_issues.py", "GAPS_REPORT.md", "chain.json")


def H(*parts) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(p if isinstance(p, bytes) else p.encode())
    return h.hexdigest()


def corpus_files():
    out = []
    for repo in REPOS:
        root = os.path.join(BASE, repo)
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
            for f in filenames:
                if any(s in f for s in SKIP):
                    continue
                rel = os.path.relpath(os.path.join(dirpath, f), root)
                if rel.startswith(".") or rel.endswith((".pyc", ".o")):
                    continue
                out.append(f"{repo}/{rel}")
    # THE HISTORY + the registry itself are history too: the ledger
    # must cover its own inputs, or the record can be edited unseen.
    for dirpath, dirnames, filenames in os.walk(os.path.join(BASE, "registry")):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for f in filenames:
            if f in ("chain.json",) or f.endswith((".pyc", ".o")):
                continue
            rel = os.path.relpath(os.path.join(dirpath, f),
                                  os.path.join(BASE, "registry"))
            out.append(f"registry/{rel}")
    # the history renderer and its output are history too
    for f in ("tools/wubu_history.py", "tools/wubu_timeline.py"):
        if os.path.exists(os.path.join(BASE, f)):
            out.append(f)
    return sorted(out)


def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot_files():
    snaps = {}
    for rel in corpus_files():
        repo, _, sub = rel.partition("/")
        path = os.path.join(BASE, repo, sub)
        if os.path.exists(path):
            snaps[rel] = file_hash(path)
    return snaps


def load_chain():
    if not os.path.exists(LEDGER_FILE):
        return []
    with open(LEDGER_FILE) as f:
        return json.load(f)


def save_chain(chain):
    os.makedirs(LEDGER, exist_ok=True)
    with open(LEDGER_FILE, "w") as f:
        json.dump(chain, f, indent=2)


def compute_root(prev_root, hashes):
    acc = prev_root or ""
    for rel in sorted(hashes):
        acc = H(acc, rel, hashes[rel])
    return H(acc)


def cmd_snapshot():
    hashes = snapshot_files()
    chain = load_chain()
    prev_root = chain[-1]["root"] if chain else ""
    root = compute_root(prev_root, hashes)
    entry = {
        "index": len(chain) + 1,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "prev_root": prev_root,
        "files": len(hashes),
        "root": root,
        "hashes": hashes,
    }
    chain.append(entry)
    save_chain(chain)
    print(f"SNAPSHOT {entry['index']}: {len(hashes)} files → {root}")
    if prev_root:
        print(f"  chained from {prev_root[:16]}…")
    return 0


def cmd_verify():
    chain = load_chain()
    if not chain:
        print("EMPTY: no snapshots yet. Run `snapshot` first.")
        return 1
    latest = chain[-1]
    # 1. the ledger itself must be unbroken (stop old-snapshot edits)
    for i, e in enumerate(chain):
        expected_prev = chain[i - 1]["root"] if i > 0 else ""
        if e["prev_root"] != expected_prev:
            print(f"✗ CHAIN BREAK at snapshot {e['index']}: a past "
                  f"snapshot was modified")
            return 1
    # 2. current state vs latest snapshot (stop file edits)
    hashes = snapshot_files()
    cur_root = compute_root(latest["prev_root"], hashes)
    if cur_root == latest["root"]:
        print(f"VERIFY OK: {len(hashes)} files match snapshot "
              f"{latest['index']} ({latest['time']})")
        return 0
    changed = []
    for rel in sorted(set(hashes) | set(latest["hashes"])):
        old = latest["hashes"].get(rel)
        new = hashes.get(rel)
        if old != new:
            changed.append(rel)
    print(f"✗ VERIFY FAILED: {len(changed)} file(s) differ from "
          f"snapshot {latest['index']}:")
    for rel in changed[:20]:
        print(f"  - {rel}")
    if len(changed) > 20:
        print(f"  … and {len(changed) - 20} more")
    print("  run `snapshot` to record the new state, or `diff` to "
          "trace history")
    return 1


def cmd_history():
    chain = load_chain()
    if not chain:
        print("EMPTY: no snapshots yet.")
        return 0
    print(f"{'N':>3}  {'TIME':<19}  {'FILES':>5}  ROOT")
    for e in chain:
        print(f"{e['index']:>3}  {e['time']:<19}  {e['files']:>5}  "
              f"{e['root'][:24]}…")
    print(f"\nLatest root: {chain[-1]['root']}")
    print("Publish this root. Any edit to any file breaks it.")
    return 0


def cmd_check():
    """Full chain integrity: every snapshot recomputes to its root."""
    chain = load_chain()
    if not chain:
        print("EMPTY")
        return 1
    bad = 0
    for i, e in enumerate(chain):
        expected_prev = chain[i - 1]["root"] if i > 0 else ""
        if e["prev_root"] != expected_prev:
            print(f"✗ snapshot {e['index']}: prev_root tampered")
            bad += 1
        r = compute_root(e["prev_root"], e["hashes"])
        if r != e["root"]:
            print(f"✗ snapshot {e['index']}: root does not match "
                  f"its stored hashes")
            bad += 1
    if bad == 0:
        print(f"CHAIN OK: {len(chain)} snapshots, every root "
              f"recomputed true")
    return 0 if bad == 0 else 1


def cmd_diff(a, b):
    chain = load_chain()
    if not (1 <= a <= len(chain)) or not (1 <= b <= len(chain)):
        print(f"CHAIN HAS {len(chain)} SNAPSHOTS")
        return 1
    ea, eb = chain[a - 1], chain[b - 1]
    ha, hb = ea["hashes"], eb["hashes"]
    added, removed, changed = [], [], []
    for rel in sorted(set(ha) | set(hb)):
        if rel not in ha:
            added.append(rel)
        elif rel not in hb:
            removed.append(rel)
        elif ha[rel] != hb[rel]:
            changed.append(rel)
    print(f"DIFF snapshot {a} ({ea['time']}) → {b} ({eb['time']}):")
    print(f"  added   : {len(added)}")
    print(f"  removed : {len(removed)}")
    print(f"  changed : {len(changed)}")
    for rel in added[:15]:
        print(f"    + {rel}")
    for rel in removed[:15]:
        print(f"    - {rel}")
    for rel in changed[:25]:
        print(f"    ~ {rel}  {ha[rel][:10]}… → {hb[rel][:10]}…")
    return 0


def cmd_find(rel):
    chain = load_chain()
    hits = []
    prev_h = None
    for e in chain:
        h = e["hashes"].get(rel)
        if h != prev_h:
            hits.append((e["index"], e["time"], prev_h, h))
            prev_h = h
    if not hits:
        print(f"{rel}: not in any snapshot")
        return 1
    print(f"{rel}:")
    for idx, ts, old, new in hits:
        state = "added" if old is None else (
            "removed" if new is None else "changed")
        print(f"  {idx:>3} {ts}  {state:7}  "
              f"{(old or '—')[:10]} → {(new or '—')[:10]}")
    return 0


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "history"
    if cmd == "snapshot":
        return cmd_snapshot()
    if cmd == "verify":
        return cmd_verify()
    if cmd == "history":
        return cmd_history()
    if cmd == "check":
        return cmd_check()
    if cmd == "diff" and len(args) == 3:
        return cmd_diff(int(args[1]), int(args[2]))
    if cmd == "find" and len(args) == 2:
        return cmd_find(args[1])
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
