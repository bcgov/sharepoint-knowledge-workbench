#!/bin/bash
# Re-audit every skill under plugins/ and refresh the audit-derived sections of
# docs/reports/skill-standard-alignment/tracker.md (per-skill table, per-plugin progress, summary, rule counts).
# "Retrofitted" state comes from temp/skill-retrofitting/retrofitted.txt. Run from anywhere inside the repo.
# It does NOT edit the Change log or Decisions sections: edit those by hand.
set -e
R=$(git rev-parse --show-toplevel); cd "$R"
T=temp/skill-retrofitting; W=$T/.work; mkdir -p "$W"
F=docs/reports/skill-standard-alignment/tracker.md
AUDIT=.agents/skills/audit-skill/scripts/audit_skill.py
FIXED=" sharepoint-audit-list-content sharepoint-remediate-field-image-references sharepoint-convert-aspx-pages sharepoint-generate-conversion-report sharepoint-copy-page-between-sites sharepoint-scaffold-spfx-listview-command-set sharepoint-scaffold-spfx-react-app sharepoint-setup-spfx-workbench "
RP=" $(grep '^plugin ' $T/retrofitted.txt | awk '{print $2}' | tr '\n' ' ')"
RS=" $(grep '^skill ' $T/retrofitted.txt | awk '{print $2}' | tr '\n' ' ')"
python3 $AUDIT . --all --mode source > "$W/cur.txt" 2>&1 || true
awk -v root="$R/plugins/" '
/^(PASS|FAIL) /{ if(p!=""){print p"\t"s"\t"e"\t"w"\t"r}; s=$1; p=$2; sub(root,"",p); e=0; w=0; r=""; next }
/^  error /{e++; match($0,/error [a-z.-]+/); t=substr($0,RSTART+6,RLENGTH-6); if(index(r,t)==0) r=r (r==""?"":",") t; next}
/^  warning /{w++; match($0,/warning [a-z.-]+/); t=substr($0,RSTART+8,RLENGTH-8); if(index(r,t)==0) r=r (r==""?"":",") t; next}
END{ if(p!="") print p"\t"s"\t"e"\t"w"\t"r }' "$W/cur.txt" | sed 's#/skills/#\t#' | sort > "$W/now.tsv"
sed 's#/skills/#\t#' $T/baseline.tsv | sort > "$W/base.tsv" 2>/dev/null || cp $T/baseline.tsv "$W/base.tsv"
awk -F'\t' -v OFS='\t' 'NR==FNR{b[$1"|"$2]=$3" "$4"/"$5; next} {k=$1"|"$2; print $1,$2,b[k],$3" "$4"/"$5,$6}' "$W/base.tsv" "$W/now.tsv" > "$W/join.tsv"
while IFS=$'\t' read -r plug skill base now open; do
  lines=$(wc -l < plugins/$plug/skills/$skill/SKILL.md | tr -d ' ')
  ts=$([ -f plugins/$plug/skills/$skill/evals/task-success.json ] && echo yes || echo no)
  if [[ "$RP" == *" $plug "* || "$RS" == *" $skill "* ]]; then st="Retrofitted"; open=$(echo "$open" | sed 's/navigation.canonical-headings,\?//; s/,$//'); elif [[ "$FIXED" == *" $skill "* ]]; then st="Errors fixed"; else st="Not started"; fi
  echo "| $plug | $skill | $lines | $base | $now | $st | $ts | ${open:-none} |"
done < "$W/join.tsv" > "$W/rows.md"
python3 - "$F" "$W/rows.md" "$W/cur.txt" <<'E'
import sys,re
p,rows,cur=sys.argv[1:4]
t=open(p).read(); r=open(rows).read(); c=open(cur).read()
i=t.index('| Plugin | Skill | Lines |'); j=t.index('## Decisions and open questions')
t=t[:i]+'| Plugin | Skill | Lines | Baseline | Now | State | Task-success evals | Open rules (excluding heading warnings for retrofitted) |\n|---|---|---|---|---|---|---|---|\n'+r+'\n'+t[j:]
cnt={}
for line in r.strip().split('\n'):
    cells=[x.strip() for x in line.strip('|').split('|')]
    pl,st=cells[0],cells[5]; d=cnt.setdefault(pl,{'n':0,'Retrofitted':0,'Errors fixed':0,'Not started':0}); d['n']+=1; d[st]+=1
tab='| Plugin | Skills | Retrofitted | Errors fixed only | Not started |\n|---|---|---|---|---|\n'+''.join(f"| {k} | {v['n']} | {v['Retrofitted']} | {v['Errors fixed']} | {v['Not started']} |\n" for k,v in sorted(cnt.items()))
a=t.index('| Plugin | Skills | Retrofitted'); b=t.index('Statuses: **Retrofitted**')
t=t[:a]+tab+'\n'+t[b:]
npass=len(re.findall(r'^PASS ',c,re.M)); nfail=len(re.findall(r'^FAIL ',c,re.M)); ne=len(re.findall(r'^  error ',c,re.M)); nw=len(re.findall(r'^  warning ',c,re.M))
t=re.sub(r'\| Passing \| 93 \| \d+ \|',f'| Passing | 93 | {npass} |',t); t=re.sub(r'\| Failing \| 11 \| \d+ \|',f'| Failing | 11 | {nfail} |',t)
t=re.sub(r'\| Errors \| 16 \| \d+ \|',f'| Errors | 16 | {ne} |',t); t=re.sub(r'\| Warnings \| 643 \| \d+ \|',f'| Warnings | 643 | {nw} |',t)
for rule in ['navigation.canonical-headings','size.lean','packaging.folder-structure','evals.missing','navigation.entry-toc','navigation.reference-toc','navigation.legacy-headings','navigation.direct-reference','links.resolve','packaging.resource','metadata.description']:
    n=len(re.findall(rf'^  [a-z]+ {re.escape(rule)}:',c,re.M))
    t=re.sub(rf'(\| `{re.escape(rule)}` \| \d+ \| )\d+( \|)',rf'\g<1>{n}\2',t)
open(p,'w').write(t)
print(f"audit: PASS {npass} FAIL {nfail} errors {ne} warnings {nw}")
E
