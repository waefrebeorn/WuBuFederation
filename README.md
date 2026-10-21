# WuBuFederation — the layer the seven organs share

> **The ~ WuBu ~ space keeps one truth and many copies. This repository is
> the truth: the registry, the federation tools, and every index generated
> from them.**

The government of the ~ WuBu ~ space has seven organs, and each organ is its
own repository:

| Organ | Repository |
|-------|------------|
| the State | [WuBuGov](https://github.com/waefrebeorn/WuBuGov) |
| the Record | [WuBuTimeline](https://github.com/waefrebeorn/WuBuTimeline) |
| the Bureau | [WuBuIntel](https://github.com/waefrebeorn/WuBuIntel) |
| the Mind | [WuBuResearch](https://github.com/waefrebeorn/WuBuResearch) |
| the Registry | [WuBuCitizen](https://github.com/waefrebeorn/WuBuCitizen) |
| the Ledger | [WuBuEconomics](https://github.com/waefrebeorn/WuBuEconomics) |
| the Hands | [WuBuCore](https://github.com/waefrebeorn/WuBuCore) |

Every organ reads the same three files. Until now those files lived only on
one machine. They live here.

## What is in here

| Path | What it is |
|------|------------|
| `registry/filings.json` | **The single source of truth** (GOV-18). Every filing, its file, its tools, its cross-references. |
| `registry/tools.json` | Every tool: its Python oracle, C11 module, CLI, and test. |
| `registry/divisions.json` | The seven organs. |
| `registry/seal.json` | The corpus seal (GOV-77): SHA-256 of every registered document, one root hash. |
| `registry/seal-history.jsonl` | The seal chain: each seal records the root before it. Append-only. |
| `tools/` | The federation tools — `govgen` (audit, seal, index, lang), the timeline tools, the research engine, the worm, the token tools. |
| `research/` | The research corpus and the wiki pages. |
| `game/` | Worm state. |
| `INDEX.md`, `PROJECT_TIMELINE.md`, `CORPUS-LANG.md`, `THE_VIEWS.md`, `THE_FORCES.md`, `GAP_EVENTS.md`, `WuBuTimeLine.md` | Generated artifacts. Regenerate them; never hand-edit them. |

The seven organ repositories sit beside this one on disk and are listed in
`.gitignore` — they are separate histories on purpose.

## The gates

Run these before any push. Green means green because red was proven
possible: `tools/test_govgen.py` plants each defect and requires the audit
to catch it.

```bash
python3 tools/govgen.py audit        # eight gates over registry + corpus
python3 tools/govgen.py seal         # reseal after an intended edit
python3 tools/govgen.py verify-seal  # recompute the seal from disk
python3 tools/govgen.py index        # regenerate every index
python3 tools/govgen.py lang         # FRES + STE + Chinese language gates
python3 tools/govgen.py check        # audit + gate tests + all WuBuCore suites
```

The rule (GOV-77): edit, reseal, audit, then push.

## The audit found this repository

The first depth audit of the space ran on 2026-10-21 and reported 274
defects. All 274 were real. The registry had lost 41 filings, 19 filings
carried the wrong number, 110 files were uncommitted across the organs, and
this layer had no version history at all. The repair is in the history, and
the doctrine that came out of it is
[GOV-77 — The Integrity Doctrine](https://github.com/waefrebeorn/WuBuGov/blob/main/docs/integrity-doctrine.md).

## Contact

WaefreBeorn — [waefrebeorn.org](https://waefrebeorn.org) · eman56447@gmail.com

The license is the umbrella license, and §14 — the Penny Clause — applies:
physical pennies only, one per human, the shipping-weight exception, and
mega-corporations owe one hundred per use.

*Filed. Done. Next.*
