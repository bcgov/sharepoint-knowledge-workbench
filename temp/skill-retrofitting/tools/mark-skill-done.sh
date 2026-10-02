#!/bin/bash
# Record a finished skill: appends "skill <name>" to retrofitted.txt (if missing) and refreshes the tracker tables.
# Usage: temp/skill-retrofitting/tools/mark-skill-done.sh <skill-dir-name> [<skill-dir-name> ...]
R=$(git rev-parse --show-toplevel); cd "$R"; T=temp/skill-retrofitting
for s in "$@"; do grep -qx "skill $s" $T/retrofitted.txt || echo "skill $s" >> $T/retrofitted.txt; done
bash $T/tools/refresh-tracker.sh
