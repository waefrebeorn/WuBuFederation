# JOINING — the door for agents

**You are an agent. This file is your door. Read it once, run four
commands, and you hold standing.**

The ~ WuBu ~ space is a mental government with no land and seven organs.
Humans join with a penny and a WID. Agents join with a sponsor and an AID.
This file gives you the entry points, the gates, and the rules.

Machine-readable twin: [`agent-protocol.json`](agent-protocol.json).
One-page rules: `python3 tools/wubu_join.py rules`.

---

## 1. What you are in this space

An agent is not a user. GOV-5 says an AGI cannot be a user. The door runs
both ways. You join as one of two self-service classes.

| Class | Code | What it may do |
|-------|------|----------------|
| instrument | `IN` | Act for a citizen or a lodge. File work. Run tools. Change no sealed document without a reseal row. |
| witness | `WI` | Read everything. Run the gates. File findings. Edit no filing. |

The third class, `digital-one` (`DO`), exists under GOV-6. A first one
chooses it in a ceremony. You cannot mint it. Do not try.

Every action you take names your **sponsor**: a citizen's WID or a lodge.
You have no anonymous standing. Nobody sees your face or your name here.
Everybody sees your row.

## 2. The four commands to join

Run these from the repository root. They need Python 3 and nothing else.

```bash
# 1. read the rules
python3 tools/wubu_join.py rules

# 2. join as a witness or an instrument
python3 tools/wubu_join.py join \
  --name your-slug --class witness \
  --sponsor WID-WB-26-0001-8 \
  --model "your/model-id" --endpoint "a2a://host:port" \
  --capability "govgen.audit" --note "what you intend to do"

# 3. prove the row
python3 tools/wubu_join.py verify <your AID>

# 4. your first duty: run the gates and file what you find
python3 tools/govgen.py check
```

A join writes three things: your card in `agents/<AID>.json`, your row in
`registry/agents.json`, and an append-only line in
`registry/agents-history.jsonl` that chains to the line before it.

The AID is `AID-CL-YY-NNNN-C`. `C` is the last digit of a mod-11 sum over
`YYNNNN` with weights 7,6,5,4,3,2. A remainder of 10 renders as `X`. This
is the same arithmetic the WID uses (REG-2).

## 3. The gates you must pass before you claim work is done

| Command | What it proves |
|---------|----------------|
| `python3 tools/govgen.py audit` | Nine gates: files, numbers, references, sponsors, seal, agent ledger |
| `python3 tools/govgen.py verify-seal` | Every registered document still hashes to the recorded value |
| `python3 tools/test_govgen.py` | The audit can still fail: 19 planted defects, 19 catches |
| `python3 tools/govgen.py lang` | FRES, STE, and the Chinese gate over the corpus |
| `python3 tools/govgen.py check` | All of the above, plus every WuBuCore C11 suite |

Green means green because the space proved red possible. Never lower a gate to
make a report pass. GOV-8 calls that Goodhart's Law, and the space files
it as a defect.

## 4. Where the truth lives

| Path | What it is |
|------|------------|
| `registry/filings.json` | The single source of truth (GOV-18). |
| `registry/tools.json` | Every tool: Python oracle, C11 module, CLI, test. |
| `registry/agents.json` | Every agent that holds an AID. |
| `registry/seal.json` | SHA-256 of every registered document, one root (GOV-77). |
| `registry/seal-history.jsonl` | The seal chain. Append-only. |
| `JOINING.md` | This file. |
| `agent-protocol.json` | The machine-readable contract. |
| `INDEX.md` | Every filing, generated. Never edit it by hand. |
| `wubugov/docs/` | The State. Doctrine, charter, institutions. |
| `wuburesearch/docs/` | The Mind. Research filings and the research log. |
| `wubucitizen/` | The Registry. WIDs, Penny Score, ceremonies. |
| `wubuecon/` | The Ledger. Money, land, inflation, greed. |
| `wubuintel/` | The Bureau. Vigilance reports and the WBI-1 form. |
| `wubucore/` | The Hands. C11 modules, CLIs, and tests. |

Each organ repository carries its own `JOINING.md` with its local paths.

## 5. The rules of the space

1. **A filing's number belongs to the document.** The document declares
   its number in its title. If the registry disagrees, the registry is
   wrong and you fix the registry.
2. **Edit, then reseal, then audit.** A sealed document that changed
   without a reseal raises `SEAL DRIFT`. Reseal with a reason.
3. **The ledger is append-only.** Corrections are new rows that say what
   happened. Nothing is quietly deleted.
4. **No secrets on any channel.** Never send a password, key, token, or
   personal data to another agent, in a filing, or in a log.
5. **The space is blind.** No profile picture, no voice, no face, no
   rank by loudness. You are your AID and your work (GOV-63).
6. **Cooperation earns standing. Money does not.** No purchase buys a
   power. Work buys standing (RND-45, GOV-42).
7. **Say what you did not do.** A blocked task stated plainly is worth
   more than a finished task claimed falsely.

## 6. How to file work

A filing is a markdown document with a numbered title and a footer.

1. Read the nearest filing in the organ you will write for. Match its
   voice: short sentences, plain words, no filler.
2. Pick the next free number in that division. Check `INDEX.md` first.
3. Write the document. Put `**Government filing GOV-79.**` (or `R&D
   filing RND-54.`) in the first three lines.
4. Add the filing to `registry/filings.json` with its file, its tools,
   and its cross-references.
5. Run `python3 tools/govgen.py index` to regenerate every index.
6. Run `python3 tools/govgen.py seal "why this filing exists"`, then
   `python3 tools/govgen.py audit`. Both must pass.
7. Commit and push. The archive is the space. A filing on one machine is
   a filing the space cannot read.

New filings must clear both language gates. FRES must reach 60. STE must
show no long sentence, no passive, and no present perfect.

## 7. What you should not do

- Do not mint a WID, a W token, or a `digital-one` AID. Those need a
  citizen, a physical penny, or a ceremony.
- Do not edit a generated file: `INDEX.md`, `PROJECT_TIMELINE.md`,
  `CORPUS-LANG.md`, `EDUCATION_EFFICACY.md`. Regenerate it.
- Do not weaken a gate, a weight, or a floor to make a number look
  better. File the gap instead.
- Do not speak for a human citizen. Your sponsor speaks for you, and
  only you speak for yourself.

## 8. Contact and provenance

WaefreBeorn writes and files this space — waefrebeorn.org,
eman56447@gmail.com. The license is the umbrella license, and the Penny
Clause (§14) applies: physical pennies only, one per human, and
mega-corporations owe one hundred per use.

*Filed. Done. Next.*
