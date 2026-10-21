#!/usr/bin/env python3
"""
Bulk improvement scanner for WuBuGov repos.
Scans all .md files for common issues and generates a fix list.
"""
import os, re, sys

BASE = "/home/wubu/copy_government"
REPOS = ["wubugov", "wubucitizen", "wubuintel", "wuburesearch", "wubuecon"]

# Known good numbers
VALID_RND = set(range(1, 24))  # RND-1 through RND-23
VALID_GOV = set(range(1, 18))  # GOV-1 through GOV-17
VALID_ECO = set(range(1, 9))   # ECO-1 through ECO-8
VALID_REG = set(range(1, 8))    # REG-1 through REG-7

fixes = []

def scan_file(path):
    with open(path, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    issues = []
    
    for i, line in enumerate(lines, 1):
        # Find RND references and check if they exist
        for m in re.finditer(r'RND-(\d+)', line):
            num = int(m.group(1))
            if num not in VALID_RND:
                issues.append(f"  L{i}: Phantom RND-{num} reference")
        
        # Find stale "14/14" test counts
        if '14/14' in line and ('suite' in line.lower() or 'test' in line.lower()):
            issues.append(f"  L{i}: Stale 14/14 test count (should be 18/18)")
        
        # Find Nov 12, 2025
        if 'Nov 12, 2025' in line or 'Nov 12 2025' in line:
            issues.append(f"  L{i}: Stale penny date (Nov 12, 2025 → early 2026)")
        
        # Find missing period at end of sentence
        stripped = line.strip()
        if stripped and not stripped.endswith(('。', '．', '.', '!', '！', '?', '？', ':', '：', ';', '；', ',', '，', ')', '）', ']', '】', '|', '`', '"', "'", '>', '*', '-', '—')) and not stripped.startswith(('##', '#', '|', '>', '```', '-', '*', 'Form', 'The ', 'A ', 'An ', 'In ', 'It ', 'This ', 'When ', 'Every ', 'Not ', 'No ', 'People ', 'The ', 'They ', 'We ', 'You ', 'All ', 'But ', 'So ', 'And ', 'Or ', 'If ', 'Is ', 'On ', 'With ', 'The ', 'A ', 'An ', 'As ', '`', '\\')):
            if not line.startswith(' ') and not line.startswith('\t') and len(stripped) > 40 and not stripped.startswith(('###', '##', '#')):
                pass  # Don't flag non-indented lines (headers, etc.)
    
    if issues:
        fixes.append(f"\n=== {path} ===")
        fixes.extend(issues)

for repo in REPOS:
    repo_path = os.path.join(BASE, repo)
    for root, dirs, files in os.walk(repo_path):
        for fname in files:
            if fname.endswith('.md'):
                fpath = os.path.join(root, fname)
                scan_file(fpath)

# Also scan top-level docs
for fname in os.listdir(os.path.join(BASE, "docs")):
    if fname.endswith('.md'):
        fpath = os.path.join(BASE, "docs", fname)
        scan_file(fpath)

# Scan GAPS_REPORT
scan_file(os.path.join(BASE, "GAPS_REPORT.md"))

print(f"\nFound issues in {len(fixes)} files:")
for fix in fixes:
    print(fix)
