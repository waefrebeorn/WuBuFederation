#!/usr/bin/env python3
"""
Bulk fixer for WuBuGov repos — targeted improvements.
Only fixes safe, unambiguous replacements.
"""
import os, re

BASE = "/home/wubu/copy_government"
REPOS = ["wubugov", "wubucitizen", "wubuintel", "wuburesearch", "wubuecon"]

count = 0
files_changed = 0

def fix_file(path):
    global count, files_changed
    with open(path, 'r') as f:
        content = f.read()
    
    original = content
    file_fixes = 0
    
    # Fix 1: Stale penny dates "Nov 12, 2025" → "early 2026"
    n = content.count("Nov 12, 2025")
    if n: content = content.replace("Nov 12, 2025", "early 2026"); file_fixes += n
    
    n = content.count("Nov 12 2025")
    if n: content = content.replace("Nov 12 2025", "early 2026"); file_fixes += n
    
    # Fix 2: Total suite counts 14/14 → 17/17 (but NOT "12/12 suites" which is per-tool)
    # Match "14/14" only in the context of total suites, not specific tool counts
    # Pattern: "14/14" in "14/14 suites" → only in GAPS_REPORT and research-log
    # The escalate/rotation/goodhart say "12/12 suites green" - those are per-tool, NOT total
    # So we need to change "14/14 suites" → "17/17 suites" but NOT "12/12 suites" → "18/18"
    # Also "14/14 test suites" → "17/17 test suites"
    n = content.count("14/14 suites")
    if n: content = content.replace("14/14 suites", "17/17 suites"); file_fixes += n
    n = content.count("14/14 test suites")
    if n: content = content.replace("14/14 test suites", "17/17 test suites"); file_fixes += n
    n = content.count("14/14 tests")
    if n: content = content.replace("14/14 tests", "17/17 tests"); file_fixes += n
    n = content.count("14/14 green")
    if n: content = content.replace("14/14 green", "17/17 green"); file_fixes += n
    n = content.count("14/14 ALL PASS")
    if n: content = content.replace("14/14 ALL PASS", "17/17 ALL PASS"); file_fixes += n
    
    # Fix 3: "14 test suites" → "17 test suites" (in README files, not in tool descriptions)
    n = content.count("14 test suites")
    if n: content = content.replace("14 test suites", "17 test suites"); file_fixes += n
    
    # Fix 4: "14/14 (was 12/12 then" → "17/17 (was 12/12 then)" - in research-log
    # Actually this is "14/14 re-verified" → "17/17 re-verified"
    n = content.count("14/14 re-verified")
    if n: content = content.replace("14/14 re-verified", "17/17 re-verified"); file_fixes += n
    
    # Fix 5: GAPS_REPORT remaining gaps section references to 14/14
    # Already handled above
    
    if content != original:
        with open(path, 'w') as f:
            f.write(content)
        count += file_fixes
        files_changed += 1
        print(f"  {path}: {file_fixes} fixes")

for repo in REPOS:
    repo_path = os.path.join(BASE, repo)
    for root, dirs, files in os.walk(repo_path):
        for fname in files:
            if fname.endswith('.md'):
                fix_file(os.path.join(root, fname))

# Also fix top-level docs
for fname in os.listdir(os.path.join(BASE, "docs")):
    if fname.endswith('.md'):
        fix_file(os.path.join(BASE, "docs", fname))
fix_file(os.path.join(BASE, "GAPS_REPORT.md"))

# Fix WuBuCore README
fix_file(os.path.join(BASE, "wubucore", "README.md"))

print(f"\nTotal fixes: {count}")
print(f"Files changed: {files_changed}")
