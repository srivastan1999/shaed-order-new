#!/bin/bash

# Script to push code to GitHub
# Usage: ./push_to_github.sh [repository-url]

set -e

REPO_URL="${1:-https://github.com/srivastan1999/shaed-order-elt.git}"

echo "🚀 Setting up GitHub remote and pushing code..."
echo "Repository URL: $REPO_URL"
echo ""

# Check if remote already exists
if git remote get-url origin 2>/dev/null; then
    echo "⚠️  Remote 'origin' already exists. Updating..."
    git remote set-url origin "$REPO_URL"
else
    echo "➕ Adding remote 'origin'..."
    git remote add origin "$REPO_URL"
fi

echo ""
echo "📤 Pushing to GitHub..."
echo ""

# Push to main branch
git push -u origin main

echo ""
echo "✅ Successfully pushed to GitHub!"
echo "Repository: $REPO_URL"



