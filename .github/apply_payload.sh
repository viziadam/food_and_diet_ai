#!/usr/bin/env bash
set -euo pipefail

gh api "repos/${GITHUB_REPOSITORY}/issues/1" --jq '.body' > /tmp/issue-bodies.txt
gh api --paginate "repos/${GITHUB_REPOSITORY}/issues/1/comments" --jq '.[].body' >> /tmp/issue-bodies.txt
python .github/restore_payload.py /tmp/issue-bodies.txt

rm -rf .payload .parts .patches
rm -f tmp-test.txt backend/app/modules/planning/simple.py
rm -f .github/apply_payload.sh .github/restore_payload.py .github/workflows/apply-meal-options.yml

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add -A
git commit -m "feat: add selectable meal alternatives and package-aware costs"
git push origin HEAD:meal-options-costs
