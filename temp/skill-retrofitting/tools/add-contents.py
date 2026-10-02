#!/usr/bin/env python3
"""Insert a '## Contents' block (links to every '## ' heading) right after the first '# ' title of each given Markdown file.
Skips files that already have a Contents heading, and ignores headings inside code fences. Anchors follow the auditor's rules
(lowercase, drop punctuation/symbols except - and _, spaces to hyphens, -1/-2 suffixes for duplicates).
Usage: python3 temp/skill-retrofitting/tools/add-contents.py <file.md> [<file.md> ...]"""
import re, sys, unicodedata
from collections import Counter

def slug(title, seen):
    t = re.sub(r"<[^>]*>", "", title).lower()
    s = "".join(c for c in t if not unicodedata.category(c).startswith(("P", "S")) or c in "-_").replace(" ", "-")
    n = seen[s]; seen[s] += 1
    return s + (f"-{n}" if n else "")

def process(path):
    lines = open(path, encoding="utf-8").read().split("\n")
    if any(re.match(r"^#{1,6}\s+(table of )?contents\b", l, re.I) for l in lines):
        return "already has Contents"
    fence = None; heads = []; seen = Counter(); title_idx = None
    for i, l in enumerate(lines):
        m = re.match(r"^\s*(`{3,}|~{3,})", l)
        if m:
            fence = None if (fence and m.group(1)[0] == fence[0]) else (fence or m.group(1)); continue
        if fence: continue
        if title_idx is None and re.match(r"^#\s+\S", l): title_idx = i
        h = re.match(r"^\s{0,3}(#{1,6})\s+(.+?)(?:\s+#+)?$", l)
        if h:
            sl = slug(h.group(2), seen)
            if len(h.group(1)) == 2: heads.append((h.group(2).strip(), sl))
    if title_idx is None or not heads: return "no title or no ## headings"
    block = ["", "## Contents", ""] + [f"- [{t}](#{s})" for t, s in heads]
    new = lines[:title_idx + 1] + block + lines[title_idx + 1:]
    open(path, "w", encoding="utf-8").write("\n".join(new))
    return f"added {len(heads)} entries"

for p in sys.argv[1:]:
    print(p, "->", process(p))
