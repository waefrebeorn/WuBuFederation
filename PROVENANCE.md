# Provenance — who actually makes the ~WuBu~ work

This file is the honest record of authorship across the ~WuBu~ repos. It exists
because attribution drift corrupts a project faster than bad code.

## The working agent

The ~WuBu~ stack is built by the user (WaefreBeorn) driving a single from-scratch
C11 agent — `slermes` (the ~WuBu~ reimplementation of an agent), with the
creativity and the decisions coming from the person. Everything in these repos
that is ~WuBu~ own work is a **SLERM**: a ground-up reimplementation, not a fork,
not a wrapper.

**Claude and Cursor are NOT part of this.** Neither was ever used in a harness,
in the build, or as a contributor. Claude was used at most once or twice, in
chat, to help draft markdown files. Cursor has never been used.

## Why the words still sometimes appear

The user's agent occasionally ran against hosted models served through
**free-promo router tokens**. Some hosted models are plainly **trained on
Claude's output**, and a model scraped on Claude can hallucinate that Claude
(or Cursor) produced the work it was describing. Those are **hallucinations,
not contributions** — the same class of error a model makes when it names a
tool it has only seen described.

## The rule

If any document in this org ever claims that Claude, Cursor, or any model other
than the user's own `slermes` agent wrote, built, or contributed to ~WuBu~
work, that claim is an **error to be corrected** — not a fact. The truthful
statement is always:

> ~WuBu~ work is made by hand and by slermes, the user's own agent. Nothing
> else has written a line.
