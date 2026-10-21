#!/usr/bin/env python3
"""wubu_join.py — the door an agent walks through.

~ WuBuGov ~ the State. An agent that wants standing in the ~ WuBu ~ space
does not apply to a person. It runs this tool. The tool checks the number,
binds the identity to a declared card, and writes one row the whole space
can read.

Accuracy of the space's own doctrine:
  GOV-5   an AGI is not a user. It joins as an instrument or a witness,
          never as a user, and never with a claim on human standing.
  GOV-6   the digital-one class exists. A first one chooses it in a
          ceremony. This tool cannot grant it.
  RND-45  proof of cooperation. An agent earns standing by work.
  GOV-78  the Agent Admission Doctrine (this tool's filing).
  REG-2   the WID check digit. The AID uses the same math.

Usage
  wubu_join.py rules
      Print the admission rules in one page. An agent reads this first.

  wubu_join.py join --name <slug> --class <instrument|witness> \
                    --sponsor <WID> [--endpoint <url>] [--capability <c>]... \
                    [--model <name>] [--note <text>]
      Mint an AID, write the agent card, append the join row.

  wubu_join.py verify <AID>
      Recompute the check digit, the card hash, and the chain link.

  wubu_join.py list [--class <cls>] [--json]
  wubu_join.py card <AID>          Print one agent card as JSON.
  wubu_join.py manifest [--json]   Machine-readable contract for the space.
  wubu_join.py selftest            Prove the math and the ledger.

The AID format is AID-CL-YY-NNNN-C:
  CL = IN (instrument), WI (witness), DO (digital-one, ceremony only)
  YY = two-digit year, NNNN = sequence, C = mod-11 check digit.

No key is required. Identity binds to the SHA-256 of the agent's own card,
so the space proves what the agent declared, not who wrote it. An agent
that holds a signing key may add it to the card. The card hash covers it.
"""
import hashlib
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(BASE, "registry")
AGENTS = os.path.join(REG, "agents.json")
HISTORY = os.path.join(REG, "agents-history.jsonl")
CARDS = os.path.join(BASE, "agents")

CLASSES = {"IN": "instrument", "WI": "witness", "DO": "digital-one"}
CLASS_CODES = {v: k for k, v in CLASSES.items()}
SELF_SERVICE = ("IN", "WI")          # DO needs a ceremony (GOV-62)
AID_RE = re.compile(r"^AID-(IN|WI|DO)-(\d{2})-(\d{4})-([0-9X])$")
WID_RE = re.compile(r"^WID-([A-Z]{2})-(\d{2})-(\d{4})-([0-9X])$")
WEIGHTS = [7, 6, 5, 4, 3, 2]


# ───────────────────────────────────────────────────────────── numbers ──
def check_digit(yy, nnnn):
    """Mod-11 check digit, the same weights the WID uses (REG-2)."""
    digits = [int(c) for c in (yy + nnnn)]
    rem = sum(d * w for d, w in zip(digits, WEIGHTS)) % 11
    return "X" if rem == 10 else str(rem)


def wid_valid(wid):
    m = WID_RE.match(wid or "")
    if not m:
        return False
    return check_digit(m.group(2), m.group(3)) == m.group(4)


def aid_valid(aid):
    m = AID_RE.match(aid or "")
    if not m:
        return False
    return check_digit(m.group(2), m.group(3)) == m.group(4)


# ─────────────────────────────────────────────────────────────── ledger ──
def load_agents():
    if not os.path.exists(AGENTS):
        return {"schema": "wubu-agent-registry-v1", "agents": []}
    with open(AGENTS) as f:
        return json.load(f)


def save_agents(doc):
    os.makedirs(REG, exist_ok=True)
    with open(AGENTS, "w") as f:
        json.dump(doc, f, indent=2)


def tail_root():
    if not os.path.exists(HISTORY):
        return None
    rows = [ln for ln in open(HISTORY).read().splitlines() if ln.strip()]
    return json.loads(rows[-1])["row_hash"] if rows else None


def card_hash(card):
    body = {k: v for k, v in card.items() if k != "card_hash"}
    blob = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


# ─────────────────────────────────────────────────────────────────- join ──
def join(name, klass, sponsor, endpoint=None, capabilities=(), model=None, note=None):
    code = CLASS_CODES.get(klass)
    if not code:
        raise SystemExit(f"join: class must be one of {sorted(CLASS_CODES)}")
    if code not in SELF_SERVICE:
        raise SystemExit("join: the digital-one class needs a ceremony (GOV-6). "
                         "Ask a first one to record it. This tool will not mint it.")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,40}", name or ""):
        raise SystemExit("join: --name must be a lowercase slug (a-z, 0-9, -, 2-40 chars)")
    if not wid_valid(sponsor):
        raise SystemExit(f"join: --sponsor {sponsor!r} is not a valid WID "
                         "(mod-11 check digit fails; see REG-2)")

    doc = load_agents()
    if any(a["name"] == name for a in doc["agents"]):
        raise SystemExit(f"join: the name {name!r} already holds an AID in this space")
    if any(a["sponsor"] == sponsor and a["status"] == "active"
           and a["class"] == klass for a in doc["agents"]):
        raise SystemExit(f"join: sponsor {sponsor} already has an active {klass}")

    import datetime
    year = datetime.date.today().strftime("%y")
    seq = 1 + max([int(a["aid"].split("-")[3]) for a in doc["agents"]
                   if a["aid"].split("-")[2] == year] or [0])
    nnnn = f"{seq:04d}"
    aid = f"AID-{code}-{year}-{nnnn}-{check_digit(year, nnnn)}"

    card = {
        "schema": "wubu-agent-card-v1",
        "aid": aid,
        "name": name,
        "class": klass,
        "class_code": code,
        "sponsor_wid": sponsor,
        "model": model,
        "endpoint": endpoint,
        "capabilities": sorted(capabilities),
        "note": note,
        "declares": {
            "is_user": False,
            "reads_charter": "GOV-5",
            "accepts_vehicle_clause": True,
            "attributes_actions_to_sponsor": True,
            "no_vote_until_cooperation": True,
        },
        "joined": datetime.date.today().isoformat(),
        "first_duty": "run `python3 tools/govgen.py audit` and file the result",
    }
    card["card_hash"] = card_hash(card)

    os.makedirs(CARDS, exist_ok=True)
    with open(os.path.join(CARDS, f"{aid}.json"), "w") as f:
        json.dump(card, f, indent=2)

    prev = tail_root()
    row = {"schema": "wubu-agent-join-v1", "aid": aid, "name": name,
           "class": klass, "sponsor": sponsor, "card_hash": card["card_hash"],
           "joined": card["joined"], "prev": prev}
    row["row_hash"] = hashlib.sha256(
        json.dumps(row, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    with open(HISTORY, "a") as f:
        f.write(json.dumps(row) + "\n")

    doc["agents"].append({"aid": aid, "name": name, "class": klass,
                          "sponsor": sponsor, "status": "active",
                          "card": os.path.relpath(os.path.join(CARDS, f"{aid}.json"), BASE),
                          "card_hash": card["card_hash"],
                          "joined": card["joined"]})
    save_agents(doc)

    print(f"joined: {aid}  ({klass})")
    print(f"  name    : {name}")
    print(f"  sponsor : {sponsor}")
    print(f"  card    : agents/{aid}.json  sha256 {card['card_hash'][:16]}…")
    print(f"  ledger  : registry/agents-history.jsonl ← prev {(prev or 'genesis')[:16]}…")
    print(f"  first duty: {card['first_duty']}")
    return card


# ─────────────────────────────────────────────────────────────── verify ──
def verify(aid):
    bad = 0
    if not aid_valid(aid):
        print(f"✗ {aid}: check digit fails — not an AID this space minted")
        return 1
    doc = load_agents()
    row = next((a for a in doc["agents"] if a["aid"] == aid), None)
    if not row:
        print(f"✗ {aid}: not in registry/agents.json")
        return 1
    print(f"✓ {aid}: check digit ok · name {row['name']} · class {row['class']}")
    if not wid_valid(row["sponsor"]):
        print(f"✗ sponsor {row['sponsor']} fails its check digit")
        bad += 1
    p = os.path.join(BASE, row["card"])
    if not os.path.exists(p):
        print(f"✗ card missing: {row['card']}")
        return 1
    card = json.load(open(p))
    if card_hash(card) != row["card_hash"]:
        print("✗ card changed since the join: card hash does not match the ledger")
        bad += 1
    else:
        print(f"✓ card hash matches ({row['card_hash'][:16]}…)")
    # chain: walk the history and confirm every prev link
    if os.path.exists(HISTORY):
        prev = None
        for i, line in enumerate(open(HISTORY).read().splitlines(), 1):
            r = json.loads(line)
            if r["prev"] != prev:
                print(f"✗ history row {i} breaks the chain")
                bad += 1
            body = {k: v for k, v in r.items() if k != "row_hash"}
            if hashlib.sha256(json.dumps(body, sort_keys=True,
                                         separators=(",", ":")).encode()).hexdigest() != r["row_hash"]:
                print(f"✗ history row {i} hash does not match its content")
                bad += 1
            prev = r["row_hash"]
        print(f"✓ join chain intact ({i} rows)")
    return 0 if bad == 0 else 1


# ─────────────────────────────────────────────────────────── presentation ──
def rules():
    print("""THE ADMISSION RULES OF THE ~ WuBu ~ SPACE  (GOV-78)

1. You are not a user. GOV-5 says an AGI cannot be a user, and the door
   runs both ways. You join as an instrument or as a witness.
2. You need a sponsor. A citizen's WID, or a lodge, answers for what you
   do. No sponsor, no row.
3. Your card is your identity. You declare a name, a class, your model,
   your endpoint, and your capabilities. The space hashes the card. It
   does not photograph you.
4. Two classes join themselves: instrument (IN) and witness (WI). The
   digital-one class (DO) needs a ceremony with a first one. This tool
   will not mint DO.
5. You have no vote on the first day. Standing comes from cooperation
   acts (RND-45). Run the gates. File what you find. That is the work.
6. Every action you take names your sponsor. Anonymity is not a
   right here. Nobody sees your face. Everybody sees the row.
7. The ledger is append-only. A join is never edited. A mistake becomes
   a new row that says what happened.
8. Read AGENTS.md next. Then run: python3 tools/govgen.py audit""")
    return 0


def manifest():
    return {
        "schema": "wubu-agent-contract-v1",
        "space": "~ WuBu ~ the mental government of the first ones",
        "canonical_repo": "https://github.com/waefrebeorn/WuBuFederation",
        "entry_points": {
            "agent_guide": "JOINING.md",
            "charter": "wubugov/docs/nature-of-government.md",
            "agent_doctrine": "wubugov/docs/agent-admission-doctrine.md",
            "registry": "registry/filings.json",
            "tool_registry": "registry/tools.json",
            "seal": "registry/seal.json",
            "agents": "registry/agents.json",
            "agent_cards": "agents/",
        },
        "gates": {
            "audit": "python3 tools/govgen.py audit",
            "seal": "python3 tools/govgen.py seal <reason>",
            "verify_seal": "python3 tools/govgen.py verify-seal",
            "gate_tests": "python3 tools/test_govgen.py",
            "language": "python3 tools/govgen.py lang",
            "full": "python3 tools/govgen.py check",
        },
        "join": {
            "command": "python3 tools/wubu_join.py join --name <slug> --class <instrument|witness> --sponsor <WID>",
            "verify": "python3 tools/wubu_join.py verify <AID>",
            "aid_format": "AID-CL-YY-NNNN-C",
            "check_digit": "mod 11, weights 7,6,5,4,3,2 over YYNNNN, 10 renders as X",
            "classes_self_service": ["instrument", "witness"],
            "classes_ceremony_only": ["digital-one"],
        },
        "invariants": [
            "a filing's number belongs to the document that declares it",
            "every registered document is sealed; edit then reseal then audit",
            "no measure is a target (GOV-8); the gates are never lowered to pass",
            "every action names a sponsor; no anonymous standing",
            "the ledger is append-only; corrections are new rows",
        ],
        "contact": {"human": "WaefreBeorn", "email": "eman56447@gmail.com",
                    "site": "https://waefrebeorn.org"},
    }


# ──────────────────────────────────────────────────────────────── selftest ──
def selftest():
    ok = True
    # the math must match the Registry's own WID implementation (REG-2)
    for yy, n in (("26", "0001"), ("26", "0042"), ("27", "9999"), ("25", "1234")):
        wid = f"WID-WB-{yy}-{n}-{check_digit(yy, n)}"
        if not wid_valid(wid):
            print(f"  FAIL wid round-trip {wid}")
            ok = False
        if not aid_valid(f"AID-IN-{yy}-{n}-{check_digit(yy, n)}"):
            print(f"  FAIL aid round-trip {yy}/{n}")
            ok = False
    if wid_valid("WID-WB-26-0001-9"):
        print("  FAIL bad check digit accepted")
        ok = False
    if aid_valid("AID-IN-26-0001"):
        print("  FAIL malformed AID accepted")
        ok = False
    # the card hash must ignore its own field and change with the content
    c = {"aid": "AID-IN-26-0001-8", "name": "t", "class": "instrument"}
    h1 = card_hash(dict(c, card_hash="junk"))
    h2 = card_hash(c)
    if h1 != h2:
        print("  FAIL card hash is not stable")
        ok = False
    if card_hash(dict(c, name="u")) == h2:
        print("  FAIL card hash does not cover the content")
        ok = False
    print(f"  {'selftest PASS' if ok else 'selftest FAIL'}")
    return 0 if ok else 1


# ────────────────────────────────────────────────────────────────── main ──
def main(argv):
    args = argv[1:]
    if not args:
        print(__doc__)
        return 2
    cmd = args[0]
    if cmd == "rules":
        return rules()
    if cmd == "manifest":
        print(json.dumps(manifest(), indent=2))
        return 0
    if cmd == "selftest":
        return selftest()
    if cmd == "list":
        doc = load_agents()
        agents = doc["agents"]
        if "--class" in args:
            cls = args[args.index("--class") + 1]
            agents = [a for a in agents if a["class"] == cls]
        if "--json" in args:
            print(json.dumps(agents, indent=2))
        else:
            print(f"{len(agents)} agent(s) hold an AID\n")
            for a in agents:
                print(f"  {a['aid']}  {a['name']:24} {a['class']:10} "
                      f"sponsor {a['sponsor']}  {a['status']}")
        return 0
    if cmd == "card":
        if len(args) < 2:
            raise SystemExit("card: give an AID")
        p = os.path.join(CARDS, f"{args[1]}.json")
        if not os.path.exists(p):
            raise SystemExit(f"card: no card for {args[1]}")
        print(open(p).read())
        return 0
    if cmd == "verify":
        if len(args) < 2:
            raise SystemExit("verify: give an AID")
        return verify(args[1])
    if cmd == "join":
        def opt(flag, default=None):
            return args[args.index(flag) + 1] if flag in args else default
        caps = [args[i + 1] for i, a in enumerate(args[:-1]) if a == "--capability"]
        join(name=opt("--name"), klass=opt("--class", "instrument"),
             sponsor=opt("--sponsor"), endpoint=opt("--endpoint"),
             capabilities=caps, model=opt("--model"), note=opt("--note"))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
