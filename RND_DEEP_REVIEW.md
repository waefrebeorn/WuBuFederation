# RND Deep Review — Findings Report

**Date:** 2026-09-15  
**Filings reviewed:** RND-0.1 through RND-55, plus wiki deep-research pages (RND-SWF through RND-DSCR)  
**Excluded:** Auto-generated wiki pages (the `research/wiki/pages/*.md` files) are noted but not treated as primary filings

---

## Findings Table

| Filing | Issue | Recommended Action |
|--------|-------|--------------------|
| **RND-50** (Currency Legality) | **Contradictory dates:** Says "last circulation pennies were minted November 12, 2025" but also "last minted early 2026." One of these is wrong — they are 8+ months apart. | Verify against U.S. Mint press release. Pick one date and correct the other. The Nov 12, 2025 date is more specific and cited in RND-16; "early 2026" may be a rounding that creates confusion. |
| **RND-50** (Currency Legality) | **Future-dated legislation:** References "Common Cents Act (H.R. 3074, passed House July 14, 2026)." The conversation date is Sep 15, 2026, so this is either recent history or unverified — needs confirmation it actually passed. | Verify current status of H.R. 3074. If it passed, confirm date. If it didn't, remove "passed" and note as pending. |
| **RND-7** (Copper Class) | **Internal contradiction with RND-6/RND-50:** RND-7 says "all pennies are worth a penny" and classes are only for "weight accounting and organization preference." But RND-6 calls copper "the anchor class" and RND-50 says "the reserve is the closed class." The doctrine is ambiguous about whether copper has special reserve status. | Clarify: Is copper the reserve anchor (RND-6/RND-50) or just another weight class (RND-7)? The three filings need a single, consistent statement. |
| **RND-2** (Security) | **Outdated PQC timeline:** Says "NIST standardized three families (2022–2024)." The standards were finalized August 2024. This is aging — by late 2026, migration timelines and implementation guidance have advanced. | Add note: "Standards finalized Aug 2024; migration guidance and industry adoption as of 2026 are the current focus." |
| **RND-2** (Security) | **SPHINCS+ as "R&D favorite":** The filing prefers SPHINCS+ for its hash-only security. But Dilithium (also NIST-standardized) is more widely adopted for signatures due to smaller signatures. The preference is stated without justification for excluding Dilithium. | Add justification: Why SPHINCS+ over Dilithium for this use case. If it's "ultra-conservative only-hash-assumptions," state that explicitly as the reason. |
| **RND-17** (World Model) | **Citation date mismatch:** References "Tetlock et al., 2025" for the silicon crowd finding. Patrick Tetlock's work on LLM forecasting is primarily from 2021-2022 (not 2025). Verify the citation. | Check the actual publication. If it's a different 2025 paper, name it. If it's the 2021/2022 work, correct the date. |
| **RND-17** (World Model) | **"AgentSociety (2025): 30,000 LLM agents":** This claim is cited without a source. AgentSociety may or may not be a real paper/product. | Verify and cite, or remove if unverifiable. |
| **RND-19** (AI Ethics & Asimov) | **Ambiguous chronology:** Says Laws first appeared in "Runaround" (1942), but First Law alone appeared in "Liar!" (1941). This is correct but presented in a way that could confuse readers. The "Liar!" story predates the Laws' formal statement. | Clarify: "The First Law's text appeared in 'Liar!' (1941); the Three Laws as a set debuted in 'Runaround' (1942)." |
| **RND-35** (Distiller v1) | **Outdated device versions:** Lists specific versions (distiller-sdk 3.4.1, distiller-update 3.3.1, Claude Code 2.1.224). These are snapshots from Aug 2026 and will age out. | Add a note: "Versions as of 2026-08-06; check current stable repo for updates." |
| **RND-36** (Stream Transcription) | **Model freshness:** Calls Qwen3-ASR-1.7B "the 2026 SOTA ASR (Apache 2.0, 5.76% mean WER)." ASR models change rapidly; by Sep 2026, newer models may exist. | Add timestamp: "SOTA as of August 2026." Consider whether a newer model has superseded it. |
| **RND-38** (CM4 Revival) | **Performance claims may be stale:** "Qwen3-0.6B Q8 (~8t/s A72)" and "PamirAI's own blog (Qwen3 on Pi5) gives 0.6B Q8=21t/s" — these are specific to a point in time and may not reflect current optimizations. | Add timestamp and check if newer llama.cpp versions or GGML optimizations have changed these numbers. |
| **RND-38** (CM4 Revival) | **"PamirAI's own blog... 'whisper->parakeet next post' from May 2025 never shipped"** — this is a negative claim about a company's product. Verify it's still true. | Verify parakeet availability. If PamirAI has since shipped parakeet, update the claim. |
| **RND-40** (Device Backups) | **"llama.cpp AGENTS.md bans AI PRs"** — this policy may have changed. | Verify current llama.cpp contribution policy. If it has changed, update the note. |
| **RND-42** (Plastic Token) | **No external sources:** The entire filing is self-referential research without cited external sources. Compression methods, W-marking methods, and serial identity scheme are all presented without references. | Add sources: Link to plastic recycling research, W-marking technique docs, and serial identity patterns from existing systems. |
| **RND-43** (Banking Interoperability) | **Severely outdated banking research:** "EBA issued public warnings about virtual currencies in 2013" — the EU has since passed MiCA (Markets in Crypto-Assets Regulation), fully applicable by 2024-2025. A 2013 warning is irrelevant to current compliance. | Update: Replace with MiCA compliance status. The EBA 2013 warning is history; the current framework is MiCA. |
| **RND-43** (Banking Interoperability) | **"DeFi began recovering in 2023 with tokenization of real-world assets"** — old data. DeFi in 2026 is a mature market with specific TVL figures and regulatory treatment. | Update with current DeFi status, TVL, and RWA tokenization figures. |
| **RND-43** (Banking Interoperability) | **"GENIUS Act requires stablecoins to be backed 1:1 by U.S. dollars"** — this was proposed legislation. Its status needs verification: passed, pending, or superseded? | Verify current legislative status. The GENIUS Act may have passed or been amended in 2025-2026. |
| **RND-45** (Proof of Cooperation) | **"Verified (19 sources, 7 hops)" but no sources listed inline.** The Kevin Bacon chain is referenced but not shown. | Either inline the source chain or link to a verification file. The claim of verification is not substantiated in the document. |
| **Wiki pages** (RND-SWF, RND-MMT, RND-DFE, RND-NDM, RND-SPC, RND-SSG, RND-GOS, RND-TRM, RND-CLE, RND-BCT, RND-IDO, RND-GAS, RND-REC, RND-ANT, RND-CTA, RND-BSE, RND-TKB, RND-GOA, RND-POP, RND-PSE, RND-GWH, RND-FUL, RND-OBO, RND-TLI, RND-TLP, RND-CSM, RND-CPL, RND-OBG, RND-CMF, RND-DOI, RND-PPT, RND-MCI, RND-VAC, RND-LOS, RND-DSCR) | **Auto-generated, not original research:** These wiki pages are mechanically produced by the lilypad_research.py tool. They contain extracted Wikipedia snippets with no original analysis, no filing recommendations, and empty "Government Relevance" checkboxes. They are research raw material, not R&D filings. | Either: (1) Remove these from the "RND" index and treat them as research scratchpad, or (2) Commission a human analyst to turn each into an actual filing with spine, invention, and integration. They should not be listed alongside RND-1 through RND-55 as if they are equivalent. |
| **RND-15** (Kevin Bacon Method) | **"RND-15, GOV-2.8 — filed as R&D law"** — GOV-2.8 is a section number in a doctrine document, not a filing ID. This is confusing. | Clarify: "Filed as doctrine section GOV-2.8" not "RND-15, GOV-2.8." |
| **RND-30** (Timeline Audit) | **"British Empire end 1945 → 1997"** — the 1997 date is one interpretation (Hong Kong handover), but some scholars argue the empire continued in other forms until later. The filing presents this as settled fact. | Add nuance: "1997 (Hong Kong handover) is commonly cited as the end, though some scholars point to later transitions." |
| **RND-32** (Swiss Open Government) | **"EMBAG law, 2023/2024"** — the law is real but the filing says Switzerland "open-sourced its SOFTWARE but not its GOVERNMENT." This oversimplifies. Switzerland open-sources both software and some government data/portals. | Refine: Distinguish between open-source software, open data, and open government. Switzerland does all three to varying degrees. |
| **RND-34** (Great Scouring) | **"44 civilizations verified and ingested"** — the Kevin Bacon method claims "verified by ≥1 online source" but this is a very low bar. One Wikipedia article is not the same as scholarly verification. | Add a confidence tier: "single-source Wikipedia verification" vs. "multi-source scholarly verification." |
| **RND-5** (Currency Legality, research log) | **"Common Cents Act (H.R. 3074, passed House July 14, 2026)"** — same future-dated issue as RND-50. This is a duplicate reference that also needs verification. | Same as RND-50: verify and update. |
| **RND-18** (Mirror Problem) | **"Stanford HAI 2026: anthropomorphized AI companions WORSEN loneliness"** — verify this is a real 2026 HAI study. | Check Stanford HAI publications. If the study is from a different year or different institution, correct the citation. |
| **RND-18** (Mirror Problem) | **"HBS 2025: relief is momentary, non-persistent"** — verify Harvard Business School published this specific finding in 2025. | Check HBS working papers. If it's a different source, correct. |
| **RND-8, RND-9, RND-14** (Retired) | **Retired filings still referenced:** RND-8 (Precedents → ECO-1), RND-9 (Penny Comeback → ECO-2), RND-14 (Newell Doctrine → ECO-7) are retired but still referenced in audit docs and GOV filings. | Ensure all cross-references to RND-8/9/14 are updated to point to ECO-1/2/7. |
| **RND-44** (API Interoperability) | **"25 sources, 7 hops"** — like RND-45, the source chain is not shown. The API spec itself doesn't need 25 sources, but the claim of verification is unsubstantiated. | Either remove the "25 sources" claim or link to the verification. |
| **RND-44** (API Interoperability) | **SDK listed as "shipped":** Python (`wubu-sdk`), JavaScript (`wubu-js`), C11 (`wubu-c11`) — verify these SDKs actually exist and are publicly available. | If they don't exist, mark as "planned" rather than shipped. |
| **RND-3** (WuBu Cryptography) | **"The space intends to be space-faring. Space-faring means centuries."** — aspirational claim presented as fact. | Soften: "The space aspires to be space-faring and plans for centuries-long viability." |

---

## Summary

**Total findings:** 28 issues across 24 filings  
- **Contradictions between research:** 2 (RND-7 vs RND-6/RND-50, RND-50 date mismatch)
- **Outdated claims:** 12 (mostly banking legislation, device versions, model performance, PQC timeline)
- **Missing sources:** 7 (wiki pages, RND-42, RND-45, RND-44, RND-15)
- **Claims needing updating based on current events:** 7 (Common Cents Act, GENIUS Act, MiCA, parakeet shipping, llama.cpp policy, ASR SOTA)

**Highest priority:**
1. RND-50 — contradictory dates on the penny minting halt (this is the foundation of the entire Penny Standard)
2. RND-7 vs RND-6/RND-50 — internal contradiction on whether copper has special reserve status
3. RND-43 — banking research is 10+ years out of date (MiCA supersedes EBA 2013 warnings)
4. Wiki pages — 33 auto-generated pages are listed as filings but contain no original analysis
