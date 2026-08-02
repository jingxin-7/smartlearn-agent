#!/bin/bash
set -e
cd /Users/jingxin/Documents/smartlearn-agent

# Step 1: Amend the last commit to remove co-author trailer
git commit --amend -m "feat: CLI Q&A with paragraph citation"

# Step 2: Stage and commit Section 4 tool files
git add pdf_summary.py pdf_summary_prd.md
git commit -m "feat: PDF summary tool (vibe coded)"

# Step 3: Stage and commit design doc
git add docs/design.md
git commit -m "docs: product design"

# Step 4: Push all
git push --force

echo "Done. Run 'git log --oneline -5' to verify."
