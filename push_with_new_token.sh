#!/bin/bash
# Script to push using a Personal Access Token with repo scope

echo "To push to GitHub, you need a Personal Access Token (PAT) with 'repo' scope."
echo ""
echo "Option 1: Create a new PAT:"
echo "  1. Go to: https://github.com/settings/tokens/new"
echo "  2. Name: 'shaed-order-elt-push'"
echo "  3. Select scope: 'repo' (full control of private repositories)"
echo "  4. Generate token and copy it"
echo ""
echo "Option 2: Use this command with your token:"
echo "  git remote set-url origin https://YOUR_TOKEN@github.com/srivastan1999/shaed-order-elt.git"
echo "  git push -u origin main"
echo ""
read -p "Enter your PAT token (or press Enter to skip): " TOKEN
if [ -n "$TOKEN" ]; then
    git remote set-url origin "https://${TOKEN}@github.com/srivastan1999/shaed-order-elt.git"
    git push -u origin main
else
    echo "Skipped. Please run manually with your token."
fi
