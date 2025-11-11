#!/bin/bash

# Script to push code using a Personal Access Token
# Usage: Edit this file and add your token, then run: ./push_with_token.sh

set -e

# ⚠️  REPLACE THIS WITH YOUR PERSONAL ACCESS TOKEN
# Get one from: https://github.com/settings/tokens/new
# Make sure it has 'repo' scope
TOKEN="YOUR_PERSONAL_ACCESS_TOKEN_HERE"

REPO_URL="https://${TOKEN}@github.com/srivastan1999/shaed-order-elt.git"

if [ "$TOKEN" = "YOUR_PERSONAL_ACCESS_TOKEN_HERE" ]; then
    echo "❌ Please edit this script and add your Personal Access Token"
    echo ""
    echo "1. Get a token from: https://github.com/settings/tokens/new"
    echo "2. Select 'repo' scope"
    echo "3. Edit this file and replace YOUR_PERSONAL_ACCESS_TOKEN_HERE"
    echo "4. Run this script again"
    exit 1
fi

echo "🚀 Pushing to GitHub..."
echo ""

git remote set-url origin "$REPO_URL"
git push -u origin main

echo ""
echo "✅ Successfully pushed to GitHub!"
echo "Repository: https://github.com/srivastan1999/shaed-order-elt"



