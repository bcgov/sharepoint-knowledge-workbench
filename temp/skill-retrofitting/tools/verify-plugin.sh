#!/bin/bash
# Verify one retrofitted plugin end to end. Usage: temp/skill-retrofitting/tools/verify-plugin.sh <plugin-dir-name>
# Checks: (1) --strict audit in source mode, (2) --strict audit of a materialized copy (symlinks resolved = what the
# installer ships), (3) every importable script module imports from that copy, (4) plugin tests, (5) symlink health,
# (6) marketplace source paths, (7) JSON validity of evals. Exit 1 if anything fails.
R=$(git rev-parse --show-toplevel); cd "$R"
P=plugins/$1; [ -d "$P/skills" ] || { echo "no such plugin skills dir: $P/skills"; exit 2; }
AUDIT=.agents/skills/audit-skill/scripts/audit_skill.py
W=$(mktemp -d); fail=0
echo "== 1. source --strict"
for s in $P/skills/*/; do s=${s%/}; python3 $AUDIT "$s" --mode source --strict >"$W/o.txt" 2>&1 || { echo "FAIL $(basename $s)"; grep -E "error|warning" "$W/o.txt" | head -5; fail=1; }; done
echo "== 2. installed (materialized copy) --strict"
for s in $P/skills/*/; do s=${s%/}; cp -RL "$s" "$W/"; python3 $AUDIT "$W/$(basename $s)" --mode installed --strict >"$W/o.txt" 2>&1 || { echo "FAIL $(basename $s)"; grep -E "error|warning" "$W/o.txt" | head -5; fail=1; }; done
echo "== 3. imports from the materialized copy (hyphenated CLI scripts are skipped: they cannot be imported by name)"
for s in $P/skills/*/; do b=$(basename ${s%/}); [ -d "$W/$b/scripts" ] || continue
  for f in "$W/$b"/scripts/*.py; do [ -e "$f" ] || continue; m=$(basename "$f" .py); case "$m" in *-*) continue;; esac
    (cd "$W/$b" && python3 -c "import sys; sys.path.insert(0,'scripts'); import $m" >/dev/null 2>&1) || { echo "IMPORT FAIL $b: $m (a module it imports is probably not linked into the skill's scripts/)"; fail=1; }; done; done
echo "== 4. plugin tests"
if [ -d "$P/tests" ]; then tr=$(cd "$P" && python3 -m pytest -q tests 2>&1 | tail -1); echo "$tr"; case "$tr" in *failed*|*error*) echo "TEST FAILURE"; fail=1;; esac; else echo "(no tests dir)"; fi
echo "== 5. symlinks"; python3 .agents/skills/symlink-manager/scripts/symlink_manager.py diagnose 2>&1 | grep -i -E "all links ok|broken|regular file|✗" | head -3
echo "== 6. marketplace"; python3 .agents/skills/audit-plugin/scripts/audit_marketplace_sources.py . 2>&1 | tail -1
echo "== 7. eval JSON"
for f in $P/skills/*/evals/*.json; do python3 -c "import json,sys; d=json.load(open('$f')); assert isinstance(d,list) and d" 2>/dev/null || { echo "BAD $f"; fail=1; }; done
rm -rf "$W"; [ $fail = 0 ] && echo "RESULT: OK" || { echo "RESULT: FAILED"; exit 1; }
