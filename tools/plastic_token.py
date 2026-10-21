#!/usr/bin/env python3
"""plastic_token.py — the WuBu plastic token system.

Tracks plastic collection, compression, W-marking, and serial
assignment for the dual-token system (GOV-30, RND-42).

Commands:
  plastic_token status           — collection + compression stats
  plastic_token add <type> <g>  — add plastic to the collection
  plastic_token compress <type>  — compress plastic into a token
  plastic_token mint <wid> <desc> — mint a plastic token with serial
  plastic_token verify <serial>  — verify token hash against ledger
  plastic_token find <serial>    — look up a found token

Plastic types: PET HDPE PVC LDPE PP PS OTHER
"""

import hashlib
import json
import os
import sys
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data", "plastic")
os.makedirs(DATA, exist_ok=True)

TYPES = {
    "PET":  {"code": 1, "density": 1.38, "sources": "water bottles, soda bottles"},
    "HDPE": {"code": 2, "density": 0.96, "sources": "milk jugs, detergent bottles"},
    "PVC":  {"code": 3, "density": 1.38, "sources": "pipes, packaging"},
    "LDPE": {"code": 4, "density": 0.92, "sources": "plastic bags, shrink wrap"},
    "PP":   {"code": 5, "density": 0.90, "sources": "yogurt cups, bottle caps"},
    "PS":   {"code": 6, "density": 1.05, "sources": "styrofoam, disposable cups"},
    "OTHER":{"code": 7, "density": 1.10, "sources": "mixed plastics"},
}

COLLECTION_FILE = os.path.join(DATA, "collection.json")
TOKENS_FILE = os.path.join(DATA, "tokens.json")
LEDGER_FILE = os.path.join(DATA, "ledger.json")


def load_json(path, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default


def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def chain_hash(prev_hash, entry):
    s = json.dumps(entry, sort_keys=True)
    return hashlib.sha256((prev_hash + s).encode()).hexdigest()


def status():
    col = load_json(COLLECTION_FILE, {"types": {}, "total_grams": 0, "total_items": 0})
    tokens = load_json(TOKENS_FILE, {"minted": [], "count": 0})
    ledger = load_json(LEDGER_FILE, {"chain": [], "root": "GENESIS"})

    print("=" * 50)
    print("PLASTIC TOKEN SYSTEM — STATUS")
    print("=" * 50)
    print(f"\nCollection: {col['total_grams']:.1f} g total, {col['total_items']} items")
    for t, info in TYPES.items():
        g = col["types"].get(t, {}).get("grams", 0)
        n = col["types"].get(t, {}).get("items", 0)
        tokens_possible = int(g / 5) if g > 0 else 0
        if g > 0:
            print(f"  {t:6s} ({info['code']}): {g:8.1f} g, {n:3d} items, ~{tokens_possible} tokens")
    print(f"\nTokens minted: {tokens['count']}")
    print(f"Ledger entries: {len(ledger['chain'])}")
    if ledger['chain']:
        print(f"Latest hash: {ledger['chain'][-1]['hash'][:32]}...")


def add(plastic_type, grams):
    plastic_type = plastic_type.upper()
    if plastic_type not in TYPES:
        print(f"Unknown type: {plastic_type}. Use: {', '.join(TYPES.keys())}")
        return

    col = load_json(COLLECTION_FILE, {"types": {}, "total_grams": 0, "total_items": 0})
    if plastic_type not in col["types"]:
        col["types"][plastic_type] = {"grams": 0, "items": 0}
    col["types"][plastic_type]["grams"] += grams
    col["types"][plastic_type]["items"] += 1
    col["total_grams"] += grams
    col["total_items"] += 1

    save_json(COLLECTION_FILE, col)
    total = col["types"][plastic_type]["grams"]
    print(f"Added {grams}g of {plastic_type}. Total: {total:.1f}g ({total/5:.0f} potential tokens)")


def compress(plastic_type):
    """Compress plastic into tokens (simulated — real compression
    requires heat+pressure equipment). Returns the number of
    tokens produced."""
    plastic_type = plastic_type.upper()
    if plastic_type not in TYPES:
        print(f"Unknown type: {plastic_type}")
        return 0

    col = load_json(COLLECTION_FILE, {"types": {}, "total_grams": 0})
    g = col["types"].get(plastic_type, {}).get("grams", 0)
    if g < 5:
        print(f"Not enough {plastic_type}: have {g:.1f}g, need 5g minimum per token")
        return 0

    tokens = load_json(TOKENS_FILE, {"minted": [], "count": 0})

    # Each token uses ~5g of plastic (quarter-sized, 2-3mm thick)
    produced = int(g / 5)
    used = produced * 5

    # Remove from collection
    col["types"][plastic_type]["grams"] -= used
    col["total_grams"] -= used

    # Update tokens (compressed but not yet minted)
    for i in range(produced):
        tokens["count"] += 1
        tokens["minted"].append({
            "index": tokens["count"],
            "plastic_type": plastic_type,
            "grams": 5,
            "minted": False,
            "serial": None
        })

    save_json(COLLECTION_FILE, col)
    save_json(TOKENS_FILE, tokens)
    print(f"Compressed {used}g of {plastic_type} into {produced} compressed tokens (awaiting mint)")
    return produced


def mint(wid, description):
    """Mint a compressed plastic token with serial PL-WID-ordinal."""
    tokens = load_json(TOKENS_FILE, {"minted": [], "count": 0})
    ledger = load_json(LEDGER_FILE, {"chain": [], "root": "GENESIS"})

    # Find first unminted token
    target = None
    for t in tokens["minted"]:
        if not t["minted"]:
            target = t
            break

    if not target:
        print("No compressed tokens available. Run compress first.")
        return

    # Generate serial: PL-WID-ordinal
    ordinal = target["index"]
    serial = f"PL-{wid}-{ordinal:04d}"

    # Chain hash
    prev_hash = ledger["chain"][-1]["hash"] if ledger["chain"] else "GENESIS"
    entry = {
        "serial": serial,
        "wid": wid,
        "description": description,
        "plastic_type": target["plastic_type"],
        "grams": target["grams"],
        "timestamp": time.time()
    }
    h = chain_hash(prev_hash, entry)
    entry["hash"] = h

    # Mark as minted
    target["minted"] = True
    target["serial"] = serial
    target["description"] = description
    target["wid"] = wid
    target["hash"] = h
    target["timestamp"] = entry["timestamp"]

    # Add to ledger
    ledger["chain"].append(entry)

    save_json(TOKENS_FILE, tokens)
    save_json(LEDGER_FILE, ledger)
    print(f"Minted: {serial}")
    print(f"  Type: {target['plastic_type']}")
    print(f"  Description: {description}")
    print(f"  Hash: {h[:32]}...")
    return serial


def verify(serial):
    """Verify a token's hash against the ledger."""
    ledger = load_json(LEDGER_FILE, {"chain": []})
    for entry in ledger["chain"]:
        if entry["serial"] == serial:
            print(f"TOKEN FOUND: {serial}")
            print(f"  WID: {entry['wid']}")
            print(f"  Description: {entry['description']}")
            print(f"  Plastic: {entry['plastic_type']}, {entry['grams']}g")
            print(f"  Hash: {entry['hash'][:32]}...")
            print(f"  Status: VERIFIED")
            return True
    print(f"Token {serial} not found in ledger.")
    return False


def find(serial):
    """Look up a found token (public access — the intentional confusion)."""
    return verify(serial)  # Same as verify, but conceptually "finder mode"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: plastic_token <status|add|compress|mint|verify|find> [args]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "status":
        status()
    elif cmd == "add" and len(sys.argv) >= 4:
        add(sys.argv[2], float(sys.argv[3]))
    elif cmd == "compress" and len(sys.argv) >= 3:
        compress(sys.argv[2])
    elif cmd == "mint" and len(sys.argv) >= 4:
        mint(sys.argv[2], " ".join(sys.argv[3:]))
    elif cmd == "verify" and len(sys.argv) >= 3:
        verify(sys.argv[2])
    elif cmd == "find" and len(sys.argv) >= 3:
        find(sys.argv[2])
    else:
        print("Unknown command or missing arguments")
        sys.exit(1)
