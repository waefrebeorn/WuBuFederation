# Deep Review: ECO Filings (1–8) & REG Filings (1–7)
## Contradictions, Gaps, Compliance Issues, Missing Cross-References

**Reviewer:** Hermes subagent  
**Scope:** All ECO-1..8, REG-1..7, cross-checked against GOV-1..76, filings.json, INDEX.md, GAPS_REPORT.md, scan_issues.py  
**Date:** 2026-09-15  

---

## Summary of Critical Findings

| # | Category | Severity |
|---|----------|----------|
| 1 | INDEX.md ECO mapping is entirely wrong | Critical |
| 2 | REG document header numbers conflict with filings.json | Critical |
| 3 | ECO-9 does not exist (task asked for ECO-1..9) | Critical |
| 4 | Phantom RND cross-refs (RND-8, 9, 10, 11, 12, 13, 14) | High |
| 5 | Penny production date stale in multiple filings | High |
| 6 | GOV-1.4 misattributed in ECO-8 | Medium |
| 7 | REG numbering off-by-one vs filings.json | Medium |
| 8 | Penny Score example value (782 vs 764) | Medium |
| 9 | WID check-digit description confusion | Medium |
| 10 | filings.json cross-ref arrays all empty | Medium |
| 11 | GOV-33 base-economy funding vs ECO-2 no-gouge tension | Low |

---

## Detailed Findings Table

| Filing | Issue | Type | Fix |
|--------|-------|------|-----|
| **INDEX.md** | ECO titles are shifted by 2: ECO-1 listed as "Economic Doctrine" but file is `precedents.md`; ECO-2 listed as "GOV Index" but file is `penny-comeback.md`; ECO-3 listed as "Inflation Everything" but file is `economic-doctrine.md`; ECO-4 listed as "Land Question" but file is `land-question.md` (this one is correct by coincidence); ECO-5 listed as "Newell Doctrine" but file is `inflation-everything.md`; ECO-6 listed as "Nexus Doctrine" but file is `nexus-doctrine.md` (correct); ECO-7 listed as "Penny Comeback" but file is `newell-doctrine.md`; ECO-8 listed as "Precedents" but file is `greed-index.md`. Every ECO title in INDEX is wrong. | Contradiction / Gap | Regenerate INDEX.md from filings.json with correct title mapping. ECO-1=Precedents, ECO-2=Penny Comeback, ECO-3=Economic Doctrine, ECO-4=Land Question, ECO-5=Inflation Everything, ECO-6=Nexus Doctrine, ECO-7=Newell Doctrine, ECO-8=Greed Index. |
| **INDEX.md** | REG titles are correct in INDEX but the document headers conflict with filings.json numbering (see REG rows below). | Contradiction | Ensure document headers match filings.json IDs. |
| **ECO-1..8** | `filings.json` shows all ECO filings with `"cross": []` despite every ECO filing containing extensive RND cross-references (ECO-1↔RND-8, ECO-2↔RND-9, ECO-3↔RND-10, ECO-4↔RND-11, ECO-5↔RND-12, ECO-6↔RND-13, ECO-7↔RND-14). | Missing cross-reference | Populate `cross` arrays in filings.json with the actual cross-filed RND numbers. |
| **ECO-1** | Header says "cross-filed RND-8" but RND-8 is retired (was Precedents cross-file, renumbered to ECO-1). The cross-reference is circular and the retired number should not be used. | Contradiction | Remove "cross-filed RND-8" from ECO-1 header. ECO-1 IS the canonical filing; it has no cross-file. |
| **ECO-2** | Header says "cross-filed RND-9" but RND-9 is retired (was Penny Comeback cross-file, renumbered to ECO-2). Same circular issue. | Contradiction | Remove "cross-filed RND-9" from ECO-2 header. |
| **ECO-3** | Header says "cross-filed RND-10" but RND-10 is a phantom number — it exists only as a cross-reference label, not as a filed RND form. The organization doctrine (GOV-11) only lists RND-1..4 as current. | Phantom reference | Remove "cross-filed RND-10" from ECO-3 header. ECO-3 is canonical. |
| **ECO-4** | Header says "cross-filed RND-11" — same phantom issue as RND-10. | Phantom reference | Remove "cross-filed RND-11" from ECO-4 header. |
| **ECO-5** | Header says "cross-filed RND-12" — same phantom issue. | Phantom reference | Remove "cross-filed RND-12" from ECO-5 header. |
| **ECO-6** | Header says "cross-filed RND-13" — same phantom issue. | Phantom reference | Remove "cross-filed RND-13" from ECO-6 header. |
| **ECO-7** | Header says "cross-filed RND-14" — RND-14 is explicitly retired per `filings.json` retired section. | Phantom reference | Remove "cross-filed RND-14" from ECO-7 header. This was already flagged in GAPS_REPORT but the header still carries it. |
| **ECO-8** | Header says "cross-filed GOV-1.4" but the powerlessness clause is actually in GOV-1 Article 1.3 ("voluntary and mind-only"), not 1.4 ("The Dwight vest"). | Contradiction | Change cross-reference to GOV-1.3 or simply cite "GOV-1" generally. |
| **ECO-2** | Says "last minted Nov 12, 2025" — stale date. Treasury confirmed production ceased early 2026. | Stale data | Update all occurrences of "Nov 12, 2025" to "early 2026" per Treasury FAQ. |
| **ECO-2** | References "RND-5, RND-6, RND-7" for WuBu Penny experiment — these RND numbers are not filed as standalone forms in the registry. | Phantom reference | Either create RND-5/6/7 form documents or cite the canonical Penny Standard (RND-55) directly. |
| **ECO-2** | Cites "the global rules are only the floor: legal tender laws (RND-5), the Three Metal Rules (RND-7)" — but RND-5 and RND-7 are not filed forms. | Phantom reference | Cite RND-55 (Penny Standard) and RND-50 (Currency Legality) instead. |
| **ECO-7** | Cites "RND-6" for the WuBu Penny IOU — same phantom issue. | Phantom reference | Cite RND-55 (Penny Standard) instead. |
| **ECO-1** | Cites "RND-16" for Penny Day — RND-16 is not a filed form in the registry. | Phantom reference | Cite the Penny Day filing directly or create RND-16. |
| **REG-1** | `citizenship.md` header says "REG-1" — matches filings.json. But `penny-score.md` header says "REG-3" while filings.json says REG-2 = Penny Score. | Contradiction | The REG document headers are systematically misaligned. Verify and correct all REG headers to match filings.json. |
| **REG-2** | `penny-score.md` header says "Form REG-3 — Penny Score spec" but filings.json assigns Penny Score to REG-2. The document content is correct but the header number is wrong. | Contradiction | Change `penny-score.md` header to "REG-2". |
| **REG-3** | `society-map.md` header says "Form REG-4 — Society Map" but filings.json assigns Society Map to REG-3. | Contradiction | Change `society-map.md` header to "REG-3". |
| **REG-4** | `wbi1-schema.md` header says "Form REG-5 — The WBI-1 Report Schema" but filings.json assigns WBI-1 Schema to REG-4. | Contradiction | Change `wbi1-schema.md` header to "REG-4". |
| **REG-5** | `wid-capacity-audit.md` header says "Form REG-6 — The WID Capacity Audit" but filings.json assigns it to REG-5. | Contradiction | Change `wid-capacity-audit.md` header to "REG-5". |
| **REG-6** | `wid-issuance-sla.md` header says "Form REG-7 — The WID Issuance SLA" but filings.json assigns it to REG-6. | Contradiction | Change `wid-issuance-sla.md` header to "REG-6". |
| **REG-7** | `wid.md` header says "Form REG-2 — WID spec" but filings.json assigns WID to REG-7. | Contradiction | Change `wid.md` header to "REG-7". |
| **REG-2** | `penny-score.md` line 87 says example produces "782" but tool actually produces "764." GAPS_REPORT claims this was fixed but the doc still says 782. | Contradiction | Update doc example to "→ 764/1000 Crew". |
| **REG-7** (`wid.md`) | Check digit algorithm described as "ascending weights from the right" and "distinct from ISBN-10's descending 10-to-1 scheme" — confusing wording that matches ISBN-10's right-to-left weighting description. GAPS_REPORT says this was clarified but the doc still uses ambiguous language. | Compliance / Clarity | Rewrite to: "6 digits (YYNNNN), weighted left-to-right ×7,×6,×5,×4,×3,×2; sum mod 11; X for 10." |
| **REG-5** (WBI-1 Schema) | Schema has `status` values "open, in-review, filed, closed" but `penny-score.md` (REG-2) references WBI-1 statuses "VERIFIED, ACTIONED, UNFOUNDED" — different status vocabularies. | Contradiction | Harmonize WBI-1 status values across REG-2 and REG-5. |
| **REG-6** (WID Capacity Audit) | Says "67.6 billion WIDs at current format" and "Earth-scale check: 8 billion humans fit comfortably" — but if every person has multiple WIDs (digital ones, multiple mind-countries), the ceiling could exhaust. GAPS_REPORT flags this as a vulnerability. | Gap | Add policy: WIDs are not lifetime; they can be re-issued after century boundaries, OR expand format to 5-digit sequence. |
| **REG-7** (WID Issuance SLA) | References `w_token` tool for issuance timestamps, but `w_token` is associated with GOV-19 (W Token ceremony), not WID issuance. | Contradiction | Use `wid` tool for WID issuance timestamps; reserve `w_token` for ceremony. |
| **REG-3** (Society Map) | Lists "The Economics Division" with "ECO-1..8" but uses the wrong title mapping (same INDEX.md error). | Contradiction | Update Society Map with correct ECO titles. |
| **REG-3** (Society Map) | Lists "AUD-1 F4" as a reference but AUD-1 is not a filed form in the registry. | Phantom reference | Remove or create AUD-1. |
| **GOV-33** (Base Economy) | Says "base economy is funded by the founder until Fast Track revenue, Penny Clause compliance, and corporate squeeze revenue exceed expenses." This creates a dependency on "Fast Track revenue" which is not defined in any ECO filing. ECO-2's no-gouge principle says "stabilization, never speculation" — Fast Track could conflict. | Contradiction / Gap | Define "Fast Track" in an ECO filing or remove the reference. Clarify how Fast Track complies with no-gouge. |
| **GOV-34** (Constitutional Hardline) | Article 2.1 says "No reinterpretations of the founder's idea" but ECO-7's Newell doctrine is a reinterpretation of Valve's strategy, not the founder's original idea. The hardline doctrine would forbid ECO-7 itself. | Contradiction | Amend GOV-34 to allow doctrinal evolution through the filing system, or explicitly grandfather ECO-7. |
| **GOV-1.4** | Cited by ECO-8 as "the powerlessness clause (filed from GOV-1.4)" but GOV-1.4 is the Dwight vest article. The powerlessness clause is actually GOV-1.3. | Contradiction | ECO-8 should cite GOV-1.3, not GOV-1.4. |
| **GOV-19** (W Token) | Says "the Mint never stamps a W Token again" and "the cap is the cap" — but also says "the stamp happens once" per ceremony. Contradiction: "never again" vs "once per ceremony." | Clarification | Reword: "The Mint stamps one W Token per ceremony; the total supply is capped at the number of ceremonies." |
| **ECO-5** (Inflation Everything) | Claims "only ~0.5% of generated information is ever attended to" citing UN "Attention Economy" brief — this statistic is not verifiable from a UN source; it appears to be from a secondary interpretation. | Compliance | Cite the original UN brief with page number, or remove the specific percentage. |
| **ECO-6** (Nexus) | Cites "Epel & Blackburn, PNAS 2004" for telomere shortening — this is correct but the filing does not include a full citation (volume, pages, DOI). | Compliance | Add full academic citation with DOI. |
| **ECO-6** | Cites "Volkow's imaging" for dopamine downregulation — no year, no paper title, no DOI. | Compliance | Add full citation. |
| **ECO-6** | Cites "Koob opponent-process" — no specific paper. Koob has many publications on opponent-process. | Compliance | Cite specific Koob paper (e.g., Koob & Le Moal, 2008 or similar). |
| **ECO-7** | Cites Gabe Newell "2009/2011 interviews" — no specific interview source, URL, or transcript. | Compliance | Add specific interview source (e.g., "Gabe Newell, TED 2010" or specific publication). |
| **ECO-4** | Cites "Friedman ('the least bad tax')" — no specific work. Friedman said this in multiple places; needs citation. | Compliance | Cite specific Friedman work (e.g., *Capitalism and Freedom* or specific interview). |
| **ECO-4** | Cites "Henry George, *Progress and Poverty* (1879)" — correct but no specific chapter or page for the "confiscate rent" quote. | Compliance | Add chapter/page for the quote. |
| **REG-1** (Citizenship) | Says "P.O. Box [TBD]" — address not filled in after extended time. | Gap | Fill in the actual P.O. Box or mark as "pending" with a filing deadline. |
| **REG-1** | Says "Class: `first-one` (default) or `digital-one` (GOV-6)" — GOV-6 is the Integration Doctrine, not the Digital One doctrine. The digital one is actually defined in GOV-6 but the citation is confusing. | Clarification | Change to "(see GOV-6, the Integration Doctrine)" — actually correct, but clarify. |
| **REG-4** (WBI-1 Schema) | Schema has `escalation` values "none, Bureau, Index, public" but ECO-8 Greed Index bands are "Filed, Watched, Flagged" — different escalation vocabularies. | Contradiction | Harmonize escalation levels across REG-4 and ECO-8. |
| **ECO-3** (Economic Doctrine) | Part 6 says "AMENDED BY GOV-19" for the W Token transition, but GOV-19 itself says it amends GOV-1 Articles I and V. The amendment chain is circular: ECO-3 is amended by GOV-19 which is amended by... | Clarification | Document the amendment chain clearly: ECO-3 Part 6 is the economic doctrine's transition; GOV-19 is the ceremony that executes it. They are complementary, not circular. |
| **ECO-2** | References "25 state laws, 20 enacted, Arizona mandates" for cash rounding — this is a time-sensitive claim that will become stale. | Gap | Add a "last verified" date and a process for updating state rounding counts. |
| **All ECO** | No ECO filing references the others by number in a consistent chain. ECO-2 references "ECO-1.1" etc. but these subsection numbers don't match the actual ECO-1 research log numbering (which is ECO-1.1, ECO-1.2, etc.). | Clarification | The subsection numbering is actually consistent within each filing, but cross-filing references should use "ECO-1 (Precedents)" not "ECO-1.1". |
| **All REG** | No REG filing references other REG filings. REG-3 (Society Map) references GOV and ECO but not REG-1, REG-2, etc. | Missing cross-reference | Add cross-references between REG filings (e.g., REG-3 should reference REG-1 for Citizenship, REG-2 for Penny Score). |
| **ECO-9** | Task asks for "ECO-1 through ECO-9" but no ECO-9 exists. `scan_issues.py` confirms `VALID_ECO = set(range(1, 9))` = ECO-1..8. filings.json has no ECO-9. | Gap | Either create ECO-9 or confirm that ECO-1..8 is the complete set. |

---

## Regulatory Compliance Issues

1. **Stale penny dates** — Multiple filings still carry "Nov 12, 2025" or outdated production figures. Treasury confirmed early 2026 cessation.
2. **Unverifiable statistics** — "0.5% of information attended to" and similar claims lack primary source citations.
3. **Incomplete academic citations** — ECO-6 and ECO-7 cite researchers without specific papers, volumes, or DOIs.
4. **TBD P.O. Box** — REG-1 has "[TBD]" for the physical address, which is required for the penny-by-mail citizenship process.
5. **WBI-1 status mismatch** — REG-4 and REG-2 use different status vocabularies for the same report type.

---

## Economic Modeling Gaps

1. **No formal model of the "special-feeling feedback loop"** — ECO-3 describes it qualitatively and simulates it (`status_loop.py`) but does not provide the exact mathematical formulation. GAPS_REPORT 2.6 flags this.
2. **No transition cost estimate** — ECO-3 Transition Doctrine says "no confiscation, no shaming, no breaking engines" but does not estimate the cost of transitioning capitalists to creators or workers to creators.
3. **No LVT revenue model** — ECO-4 advocates Land Value Tax but does not estimate revenue potential or implementation cost.
4. **No Greed Index historical calibration** — ECO-8 invents the Index (0-300) but provides no historical data to validate the band thresholds (Filed/Watched/Flagged).
5. **No Newell adoption model validation** — ECO-7 simulates "enforcement plateaus ~40%; service compounds past 95%" but these numbers are from the tool, not from empirical data.
6. **No inflation quantification** — ECO-5 describes four inflations qualitatively but does not quantify the "cost of being later" in dollar terms.
7. **Fast Track undefined** — GOV-33 relies on "Fast Track revenue" but no ECO filing defines what Fast Track is.

---

## Missing Cross-References

| From | To | Status |
|------|----|--------|
| All ECO | RND cross-files | Listed in text but not in `filings.json` `cross` arrays |
| REG-3 (Society Map) | REG-1, REG-2 | Missing |
| REG-4 (WBI-1 Schema) | ECO-8 (Greed Index) | Missing — both define escalation levels |
| REG-7 (WID SLA) | GOV-19 (W Token) | Missing — both deal with issuance timing |
| ECO-7 (Newell) | GOV-47 (Enforcement) | Missing — Newell is the anti-enforcement doctrine |
| ECO-8 (Greed Index) | REG-4 (WBI-1 Schema) | Missing — Index feeds reports to schema |
| ECO-3 (Economic Doctrine) | GOV-33 (Base Economy) | Missing — both describe economic transition |
| GOV-1.3 (Powerlessness) | ECO-8 (Greed Index) | Mis-referenced as GOV-1.4 |
| ECO-2 (Penny Comeback) | RND-55 (Penny Standard) | Should reference directly, not via phantom RND-5/6/7 |

---

## Files Reviewed

- `/home/wubu/copy_government/wubuecon/docs/economic-doctrine.md` (ECO-3)
- `/home/wubu/copy_government/wubuecon/docs/greed-index.md` (ECO-8)
- `/home/wubu/copy_government/wubuecon/docs/inflation-everything.md` (ECO-5)
- `/home/wubu/copy_government/wubuecon/docs/land-question.md` (ECO-4)
- `/home/wubu/copy_government/wubuecon/docs/newell-doctrine.md` (ECO-7)
- `/home/wubu/copy_government/wubuecon/docs/nexus-doctrine.md` (ECO-6)
- `/home/wubu/copy_government/wubuecon/docs/penny-comeback.md` (ECO-2)
- `/home/wubu/copy_government/wubuecon/docs/precedents.md` (ECO-1)
- `/home/wubu/copy_government/wubuecon/docs/research-log.md`
- `/home/wubu/copy_government/wubucitizen/docs/citizenship.md` (REG-1)
- `/home/wubu/copy_government/wubucitizen/docs/penny-score.md` (REG-2/3)
- `/home/wubu/copy_government/wubucitizen/docs/society-map.md` (REG-3/4)
- `/home/wubu/copy_government/wubucitizen/docs/wbi1-schema.md` (REG-4/5)
- `/home/wubu/copy_government/wubucitizen/docs/wid-capacity-audit.md` (REG-5/6)
- `/home/wubu/copy_government/wubucitizen/docs/wid-issuance-sla.md` (REG-6/7)
- `/home/wubu/copy_government/wubucitizen/docs/wid.md` (REG-7/2)
- `/home/wubu/copy_government/wubugov/docs/nature-of-government.md` (GOV-1)
- `/home/wubu/copy_government/wubugov/docs/w-token-doctrine.md` (GOV-19)
- `/home/wubu/copy_government/wubugov/docs/base-economy.md` (GOV-33)
- `/home/wubu/copy_government/wubugov/docs/w-mint.md` (GOV-48)
- `/home/wubu/copy_government/wubugov/docs/legal-foundation.md` (GOV-64)
- `/home/wubu/copy_government/wubugov/docs/mint-doctrine.md` (GOV-14)
- `/home/wubu/copy_government/wubugov/docs/enforcement-doctrine.md` (GOV-47)
- `/home/wubu/copy_government/wubugov/docs/zero-debt-doctrine.md` (GOV-65)
- `/home/wubu/copy_government/wubugov/docs/constitutional-hardline.md` (GOV-34)
- `/home/wubu/copy_government/wubugov/docs/organization-doctrine.md` (GOV-11)
- `/home/wubu/copy_government/wubugov/docs/criticism-audit.md` (GOV-20)
- `/home/wubu/copy_government/registry/filings.json`
- `/home/wubu/copy_government/INDEX.md`
- `/home/wubu/copy_government/GAPS_REPORT.md`
- `/home/wubu/copy_government/scan_issues.py`
- `/home/wubu/copy_government/PROJECT_TIMELINE.md`
- `/home/wubu/.hermes/skills/devops/wubugov-infrastructure/references/wubueconomics-research.md`
- `/home/wubu/.hermes/skills/devops/wubugov-infrastructure/references/wubueconomics-land-lifespan.md`

---

*Form DEEP-REVIEW — ECO/REG consistency audit. Filed. Done. Next.*
