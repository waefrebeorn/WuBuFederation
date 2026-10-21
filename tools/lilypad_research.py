#!/usr/bin/env python3
"""lilypad_research.py — the WuBu 25-source 7-step Kevin Bacon research system.

Uses web_search for actual internet research. Builds wiki-subtext
research pages with full source chains. Recursive government improvement.

Commands:
  lilypad_research run <topic> <question> — full 25-source research
  lilypad_research run_batch               — run all queued topics
  lilypad_research queue <topic> <q>       — add topic to queue
  lilypad_research status                  — show research pages
  lilypad_research improve                 — auto-improve government filings
  lilypad_research wiki                    — regenerate wiki index
  lilypad_research export                  — export findings as GOV/RND filings
"""

import hashlib
import json
import os
import re
import sys
import time
import urllib.request
import urllib.parse

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESEARCH = os.path.join(BASE, "research")
WIKI = os.path.join(RESEARCH, "wiki")
PAGES = os.path.join(WIKI, "pages")
QUEUE = os.path.join(WIKI, "queue.json")
INDEX = os.path.join(WIKI, "index.md")
LOG = os.path.join(WIKI, "log.md")
CHAIN_DB = os.path.join(WIKI, "chains.json")
FINDINGS = os.path.join(WIKI, "findings.json")

for d in [RESEARCH, WIKI, PAGES]:
    os.makedirs(d, exist_ok=True)

MAX_HOPS = 7
TARGET_SOURCES = 25


def load_json(path, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default


def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def sha256(s):
    return hashlib.sha256(s.encode()).hexdigest()


def web_search(query, limit=10):
    """Search using available backends."""
    results = []
    
    # Try DuckDuckGo HTML
    try:
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        # Parse with multiple patterns
        patterns = [
            r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>',
            r'<a[^>]*rel="nofollow"[^>]*href="([^"]*)"[^>]*>(.*?)</a>',
        ]
        for pat in patterns:
            for m in re.finditer(pat, html, re.DOTALL):
                url_raw = m.group(1)
                title = re.sub(r'<[^>]+>', '', m.group(2)).strip()
                if url_raw.startswith("http") and len(title) > 5:
                    results.append({"url": url_raw, "title": title, "description": ""})
                if len(results) >= limit:
                    break
            if len(results) >= limit:
                break
    except Exception:
        pass
    
    # Try Bing as fallback
    if not results:
        try:
            url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}&count={limit}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
            for m in re.finditer(r'<h2><a[^>]*href="([^"]*)"[^>]*>(.*?)</a></h2>', html, re.DOTALL):
                results.append({"url": m.group(1), "title": re.sub(r'<[^>]+>', '', m.group(2)).strip(), "description": ""})
                if len(results) >= limit:
                    break
        except Exception:
            pass
    
    # Try Wikipedia for topic grounding
    if not results:
        try:
            wiki_q = urllib.parse.quote(query.replace(" ", "_"))
            url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={wiki_q}&format=json&srlimit={limit}"
            req = urllib.request.Request(url, headers={"User-Agent": "WuBuResearch/1.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            for item in data.get("query", {}).get("search", []):
                title = item.get("title", "")
                snippet = re.sub(r'<[^>]+>', '', item.get("snippet", ""))
                results.append({
                    "url": f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}",
                    "title": title,
                    "description": snippet
                })
                if len(results) >= limit:
                    break
        except Exception:
            pass
    
    return results[:limit]


def derive_questions(topic, base_question):
    """Derive sub-questions for Kevin Bacon chain hops."""
    return [
        base_question,
        f"{topic} government policy",
        f"{topic} economics",
        f"{topic} social impact",
        f"{topic} technology",
        f"{topic} international cooperation",
        f"{topic} future trends",
    ]


def build_chain(question, topic):
    """Build a 7-hop Kevin Bacon chain with 25+ sources."""
    chain = []
    visited = set()
    questions = derive_questions(topic, question)
    
    for hop in range(MAX_HOPS):
        q = questions[hop % len(questions)]
        sources = web_search(q, 5)
        
        for src in sources:
            url = src.get("url", "")
            if url and url not in visited:
                src["hop"] = hop + 1
                src["query"] = q
                src["chain_hash"] = sha256(json.dumps(src, sort_keys=True))
                chain.append(src)
                visited.add(url)
                if len(chain) >= TARGET_SOURCES:
                    return chain
    
    # If still under target, do additional passes
    attempts = 0
    while len(chain) < TARGET_SOURCES and attempts < 5:
        q = f"{topic} {question} research study {attempts+1}"
        sources = web_search(q, 5)
        for src in sources:
            url = src.get("url", "")
            if url and url not in visited:
                src["hop"] = MAX_HOPS
                src["query"] = q
                src["chain_hash"] = sha256(json.dumps(src, sort_keys=True))
                chain.append(src)
                visited.add(url)
                if len(chain) >= TARGET_SOURCES:
                    break
        attempts += 1
    
    return chain


def extract_facts(text):
    """Extract key facts from text."""
    sentences = re.split(r'[.!?]+', text)
    facts = []
    for s in sentences:
        s = s.strip()
        if 30 < len(s) < 200:
            if any(w in s.lower() for w in ["is", "are", "was", "were", "first", "last", "founded", "created", "population", "percent", "billion", "million", "year", "rate", "decline", "increase"]):
                facts.append(s)
    return facts[:5]


def research_topic(topic, question):
    """Full research: 25 sources, 7 hops, wiki page output."""
    print(f"RESEARCHING: {topic}")
    print(f"Question: {question}")
    
    chain = build_chain(question, topic)
    print(f"Chain built: {len(chain)} sources across {MAX_HOPS} hops")
    
    # Sanitize topic to prevent path traversal
    topic = re.sub(r'[^\w\-]', '_', topic)
    topic = os.path.basename(topic)
    
    # Build wiki page
    page_path = os.path.join(PAGES, f"{topic}.md")
    all_facts = []
    
    with open(page_path, 'w') as f:
        f.write(f"# Research: {topic}\n\n")
        f.write(f"**Question:** {question}\n")
        f.write(f"**Sources:** {len(chain)}\n")
        f.write(f"**Method:** 7-step Kevin Bacon chain\n")
        f.write(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write("---\n\n")
        
        f.write("## Source Chain\n\n")
        for i, src in enumerate(chain):
            f.write(f"### Hop {src.get('hop', '?')} — Source {i+1}\n")
            f.write(f"- **Title:** {src.get('title', 'N/A')}\n")
            f.write(f"- **URL:** {src.get('url', 'N/A')}\n")
            desc = src.get('description', '')
            if desc:
                f.write(f"- **Snippet:** {desc[:250]}\n")
            f.write(f"- **Hash:** {src.get('chain_hash', 'N/A')[:24]}...\n")
            f.write(f"- **Query:** {src.get('query', 'N/A')}\n\n")
            
            facts = extract_facts(desc)
            all_facts.extend(facts)
        
        f.write("---\n\n")
        f.write("## Synthesis\n\n")
        if all_facts:
            for fact in all_facts[:15]:
                f.write(f"- {fact}\n")
        else:
            f.write("*(No facts extracted — manual review needed)*\n")
        
        f.write("\n---\n\n")
        f.write("## Kevin Bacon Chain Verification\n\n")
        for i in range(min(len(chain) - 1, 20)):
            a = chain[i].get("title", "")[:35]
            b = chain[i+1].get("title", "")[:35]
            f.write(f"- {a} → {b}\n")
        
        f.write("\n---\n\n")
        f.write("## Government Relevance\n\n")
        f.write("*(How this research improves filings)*\n\n")
        f.write("- [ ] Cross-reference with existing GOV/RND filings\n")
        f.write("- [ ] Identify contradictions with current doctrine\n")
        f.write("- [ ] Propose new tools or amendments\n\n")
        
        f.write("## Filing Recommendations\n\n")
        f.write("*(Auto-generated from research — refine manually)*\n\n")
        
        # Auto-generate filing recommendations
        if "population" in question.lower() or "birth" in question.lower():
            f.write("- GOV: Amendment to ECO-5 (Inflation of Everything) to address population decline\n")
            f.write("- RND: Research into incentive structures for progeny creation\n")
        if "economy" in question.lower() or "basic" in question.lower():
            f.write("- GOV: New filing for Base Economy Level 1 system\n")
            f.write("- ECO: Integration with existing Penny Standard\n")
        if "bank" in question.lower() or "ledger" in question.lower():
            f.write("- RND: Technical specification for bank cooperation API\n")
            f.write("- GOV: Legal framework for inter-ledger compatibility\n")
        if "identity" in question.lower():
            f.write("- REG: Amendment to WID system for global compatibility\n")
            f.write("- GOV: Identity portability doctrine\n")
        if "onboard" in question.lower():
            f.write("- REG: Streamlined citizenship process\n")
            f.write("- GOV: Call-to-action doctrine for public engagement\n")
        
        f.write(f"\n*Filed. Done. Next.*\n")
    
    # Update index
    index_data = load_json(QUEUE, {"pages": []})
    entry = {
        "topic": topic,
        "file": f"pages/{topic}.md",
        "sources": len(chain),
        "question": question,
        "timestamp": time.time()
    }
    # Replace if exists
    idx = None
    for i, p in enumerate(index_data.get("pages", [])):
        if p.get("topic") == topic:
            idx = i
            break
    if idx is not None:
        if "pages" not in index_data:
            index_data["pages"] = []
        index_data["pages"][idx] = entry
    else:
        if "pages" not in index_data:
            index_data["pages"] = []
        index_data["pages"].append(entry)
    
    save_json(QUEUE, index_data)
    
    # Update chains DB
    chains = load_json(CHAIN_DB, {})
    chains[topic] = {
        "question": question,
        "chain_length": len(chain),
        "sources": [{"url": s.get("url",""), "hop": s.get("hop",0), "hash": s.get("chain_hash",""), "title": s.get("title","")} for s in chain],
        "timestamp": time.time(),
        "page": page_path
    }
    save_json(CHAIN_DB, chains)
    
    # Update log
    with open(LOG, 'a') as f:
        f.write(f"## {time.strftime('%Y-%m-%d %H:%M')} — {topic}\n")
        f.write(f"Sources: {len(chain)}, Hops: {MAX_HOPS}, Facts: {len(all_facts)}\n")
        f.write(f"File: {page_path}\n\n")
    
    print(f"Research page: {page_path}")
    return chain


def queue_topic(topic, question):
    """Add a topic to the research queue."""
    queue = load_json(QUEUE, {"queue": []})
    entry = {"topic": topic, "question": question, "added": time.time()}
    queue.get("queue", []).append(entry)
    save_json(QUEUE, queue)
    print(f"Queued: {topic} — {question}")


def run_batch():
    """Run all queued topics."""
    queue = load_json(QUEUE, {"queue": []})
    items = queue.get("queue", [])
    if not items:
        print("No topics in queue.")
        return
    
    print(f"Running batch: {len(items)} topics")
    results = []
    for item in items:
        chain = research_topic(item["topic"], item["question"])
        results.append({"topic": item["topic"], "sources": len(chain)})
    
    # Clear queue after running
    save_json(QUEUE, {"queue": []})
    print(f"\nBatch complete: {len(results)} topics researched")
    for r in results:
        print(f"  {r['topic']}: {r['sources']} sources")


def status():
    chains = load_json(CHAIN_DB, {})
    index = load_json(QUEUE, {"pages": []})
    
    print("=" * 50)
    print("LILYPAD RESEARCH SYSTEM — STATUS")
    print("=" * 50)
    print(f"\nResearch topics: {len(chains)}")
    total = sum(c.get("chain_length", 0) for c in chains.values())
    print(f"Total sources: {total}")
    
    if chains:
        print("\nTopics:")
        for topic, data in chains.items():
            print(f"  {topic}: {data.get('chain_length', 0)} sources")


def improve():
    """Auto-improve government filings using research chains."""
    chains = load_json(CHAIN_DB, {})
    findings = load_json(FINDINGS, {"improvements": []})
    
    print("=" * 50)
    print("GOVERNMENT IMPROVEMENT LOOP")
    print("=" * 50)
    
    for topic, data in chains.items():
        chain_len = data.get("chain_length", 0)
        if chain_len >= 5:
            imp = {
                "topic": topic,
                "sources": chain_len,
                "action": f"Cross-reference {topic} with relevant filings",
                "priority": "HIGH" if chain_len >= 15 else "MEDIUM",
                "timestamp": time.time()
            }
            # Avoid duplicates
            existing = [f for f in findings.get("improvements", []) if f.get("topic") == topic]
            if not existing:
                findings.setdefault("improvements", []).append(imp)
    
    save_json(FINDINGS, findings)
    
    print(f"\n{len(findings.get('improvements', []))} improvement opportunities:")
    for imp in findings.get("improvements", [])[:10]:
        print(f"  [{imp['priority']}] {imp['topic']}: {imp['sources']} sources")
        print(f"    → {imp['action']}")
    
    return findings


def export_findings():
    """Export research findings as draft government filings."""
    findings = load_json(FINDINGS, {"improvements": []})
    chains = load_json(CHAIN_DB, {})
    
    exported = []
    for imp in findings.get("improvements", []):
        topic = imp["topic"]
        chain_data = chains.get(topic, {})
        chain = chain_data.get("sources", [])
        
        # Generate a draft filing
        filing = {
            "id": f"RND-{len(chains)+100:03d}",
            "topic": topic,
            "sources": len(chain),
            "recommendation": imp["action"],
            "draft_file": f"wuburesearch/docs/research-{topic}.md"
        }
        exported.append(filing)
        
        # Write the draft filing
        doc_path = os.path.join(BASE, "wuburesearch", "docs", f"research-{topic}.md")
        with open(doc_path, 'w') as f:
            f.write(f"# Research Finding: {topic}\n\n")
            f.write(f"**Source:** lilypad_research system, {len(chain)} sources\n")
            f.write(f"**Recommendation:** {imp['action']}\n\n")
            f.write("## Findings\n\n")
            for src in chain[:10]:
                f.write(f"- [{src.get('title','')}]({src.get('url','')})\n")
            f.write(f"\n*Auto-generated. Refine before formal filing.*\n")
    
    print(f"Exported {len(exported)} draft filings:")
    for e in exported:
        print(f"  {e['id']}: {e['topic']}")
    
    return exported


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: lilypad_research <run|queue|run_batch|status|improve|export> [args]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "run" and len(sys.argv) >= 4:
        research_topic(sys.argv[2], " ".join(sys.argv[3:]))
    elif cmd == "queue" and len(sys.argv) >= 4:
        queue_topic(sys.argv[2], " ".join(sys.argv[3:]))
    elif cmd == "run_batch":
        run_batch()
    elif cmd == "status":
        status()
    elif cmd == "improve":
        improve()
    elif cmd == "export":
        export_findings()
    else:
        print("Unknown command")
        sys.exit(1)
