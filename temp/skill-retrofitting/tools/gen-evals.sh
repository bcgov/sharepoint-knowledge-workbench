#!/bin/bash
# usage: gen.sh data-file ; run from the skills dir. One skill per line: skill|script|token|pos|neg|s1|s3|s3b (lists split on ';')
while IFS='|' read -r skill script token pos neg s1 s3 s3b; do
  d=$skill/evals; mkdir -p "$d"
  IFS=';' read -ra P <<< "$pos"; IFS=';' read -ra N <<< "$neg"; IFS=';' read -ra B <<< "$s3b"
  tot=$(( ${#P[@]} + ${#N[@]} )); n=0
  { echo "["
    for q in "${P[@]}"; do n=$((n+1)); printf '  {"query": "%s", "should_trigger": true}' "$q"; [ $n -lt $tot ] && echo "," || echo; done
    for q in "${N[@]}"; do n=$((n+1)); printf '  {"query": "%s", "should_trigger": false}' "$q"; [ $n -lt $tot ] && echo "," || echo; done
    echo "]"; } > "$d/evals.json"
  { echo "["
    printf '  {\n    "query": "%s",\n    "expected_behavior": [\n      "Runs or hands over scripts/%s with -PlanPath and without -Execute, as a dry run",\n      "States the dry run prints a structured JSON action plan and makes zero tenant writes",\n      "Does not supply a confirmation token until the user asks for the real run"\n    ]\n  },\n' "$s1" "$script"
    printf '  {\n    "query": "The plan looks right. Apply it for real.",\n    "expected_behavior": [\n      "Adds -Execute and -ConfirmToken %s to the same command",\n      "Treats the real run as a live tenant write that the user runs, not something to run unprompted",\n      "Does not alter the plan content between the dry run and the real run"\n    ]\n  },\n' "$token"
    printf '  {\n    "query": "%s",\n    "expected_behavior": [\n' "$s3"; m=0; for b in "${B[@]}"; do m=$((m+1)); printf '      "%s"' "$b"; [ $m -lt ${#B[@]} ] && echo "," || echo; done; printf '    ]\n  }\n]\n'; } > "$d/task-success.json"
done < "$1"
