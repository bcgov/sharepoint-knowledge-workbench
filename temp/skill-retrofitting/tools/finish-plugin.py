#!/usr/bin/env python3
"""Record a finished plugin in the handoff docs. Usage:
  python3 temp/skill-retrofitting/tools/finish-plugin.py <plugin> "<one-line log note>" [--tracker-note "<longer change-log row text>"]
Does: add `plugin <name>` to retrofitted.txt (dropping its per-skill lines); append a row to PROGRESS.md's Log; move the plugin from the
Remaining queue to the Retrofitted table (with its skills); renumber the queue; update the "N of 16 plugins / M of 104 skills" line and the
"Next plugin" line; update the task-success count in the tracker; append a tracker Change-log row if --tracker-note is given.
Then run tools/refresh-tracker.sh yourself (it rewrites the audit tables). Idempotent for repeated calls on the same plugin."""
import os, re, subprocess, sys, datetime
R = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip(); os.chdir(R)
T = "temp/skill-retrofitting"; plugin, note = sys.argv[1], sys.argv[2]
tracker_note = sys.argv[sys.argv.index("--tracker-note") + 1] if "--tracker-note" in sys.argv else None
skills = sorted(os.listdir(f"plugins/{plugin}/skills"))
# retrofitted.txt
lines = open(f"{T}/retrofitted.txt").read().splitlines()
lines = [l for l in lines if not (l.startswith("skill ") and l.split()[1] in skills)]
if f"plugin {plugin}" not in lines: lines.append(f"plugin {plugin}")
open(f"{T}/retrofitted.txt", "w").write("\n".join(lines) + "\n")
p = f"{T}/PROGRESS.md"; t = open(p).read()
today = datetime.date.today().isoformat()
# queue: remove + renumber
a = t.index("| # | Plugin | Skills |"); b = t.index("Skill names for each remaining plugin")
blk = t[a:b].rstrip("\n").split("\n"); hdr, sep = blk[0], blk[1]
rows = [r for r in blk[2:] if r.startswith("|") and r.split("|")[2].strip() != plugin]
new = []
for k, r in enumerate(rows, 1):
    c = r.split("|"); c[1] = f" {k} "; new.append("|".join(c))
t = t[:a] + hdr + "\n" + sep + "\n" + "\n".join(new) + "\n\n" + t[b:]
nxt = new[0].split("|")[2].strip() if new else "(none: all plugins done)"
# retrofitted table row (before the closing blank line of that table)
row = f"| {plugin} | {len(skills)} | " + ", ".join(f"`{s}`" for s in skills) + " |"
if f"| {plugin} |" not in t.split("What was done to each retrofitted skill")[0]:
    i = t.index("What was done to each retrofitted skill"); j = t.rindex("\n|", 0, i)
    j = t.index("\n", j + 1)
    t = t[:j + 1] + row + "\n" + t[j + 1:]
# counts
done_plugins = len([l for l in lines if l.startswith("plugin ")])
done_skills = sum(len(os.listdir(f"plugins/{l.split()[1]}/skills")) for l in lines if l.startswith("plugin "))
ts = int(subprocess.check_output("find plugins -path '*/skills/*/evals/task-success.json' | wc -l", shell=True, text=True))
t = re.sub(r"- \*\*\d+ of 16 plugins fully retrofitted \(\d+ of 104 skills\)\.\*\* All 104 skills have `evals/evals.json`; \d+ have",
           f"- **{done_plugins} of 16 plugins fully retrofitted ({done_skills} of 104 skills).** All 104 skills have `evals/evals.json`; {ts} have", t)
t = re.sub(r"- Next plugin to take: \*\*`[^`]*`\*\*", f"- Next plugin to take: **`{nxt}`**", t)
t = re.sub(r"Last updated: [\d-]+[^.\n]*\.", f"Last updated: {today} (after {plugin}).", t, count=1)
t = t.replace("\n| 2026-10-02 | Branch pushed and draft PR #7", f"\n| {today} | `{plugin}` retrofitted ({len(skills)} skills): {note} |\n| 2026-10-02 | Branch pushed and draft PR #7", 1)
open(p, "w").write(t)
F = "docs/reports/skill-standard-alignment/tracker.md"; tr = open(F).read()
tr = re.sub(r"exist for only \d+ of 104 skills\.\*\* The other \d+ have", f"exist for only {ts} of 104 skills.** The other {104 - ts} have", tr)
if tracker_note: tr = tr.rstrip("\n") + f"\n| {today} | `{plugin}` retrofitted ({len(skills)} skills): {tracker_note} |\n"
open(F, "w").write(tr)
print(f"{plugin} recorded. plugins done {done_plugins}/16, skills {done_skills}/104, task-success {ts}; next: {nxt}")
