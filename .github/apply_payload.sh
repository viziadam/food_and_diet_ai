#!/usr/bin/env bash
set -uo pipefail

gh api "repos/${GITHUB_REPOSITORY}/issues/1" --jq '.body' > /tmp/issue-bodies.txt
gh api --paginate "repos/${GITHUB_REPOSITORY}/issues/1/comments" --jq '.[].body' >> /tmp/issue-bodies.txt

set +e
python .github/restore_payload.py /tmp/issue-bodies.txt > /tmp/assembly.log 2>&1
status=$?
set -e

if [ "$status" -ne 0 ]; then
  cp /tmp/assembly.log .github/assembly-error.txt
  wc -c /tmp/issue-bodies.txt >> .github/assembly-error.txt
  grep -o "PATCH-CHUNK-[0-9]*" /tmp/issue-bodies.txt | sort -u >> .github/assembly-error.txt
  git config user.name "github-actions[bot]"
  git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
  git add .github/assembly-error.txt
  git commit -m "chore: record feature assembly error"
  git push origin HEAD:meal-options-costs
  exit "$status"
fi

rm -rf .payload .parts .patches
rm -f tmp-test.txt backend/app/modules/planning/simple.py
rm -f .github/assembly-error.txt
rm -f .github/apply_payload.sh .github/restore_payload.py
rm -f .github/workflows/apply-meal-options.yml .github/workflows/apply-on-pr.yml

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add -A
git commit -m "feat: add selectable meal alternatives and package-aware costs"
git push origin HEAD:meal-options-costs
