#!/bin/bash

# Script to create GitHub repo and push code
# This will wait for you to create the repo manually, then push

set -e

REPO_NAME="shaed-order-elt"
USERNAME="srivastan1999"
REPO_URL="https://github.com/${USERNAME}/${REPO_NAME}.git"

echo "📦 Repository Setup Script"
echo "=========================="
echo ""
echo "Repository name: $REPO_NAME"
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
echo "⏳ Waiting for repository to be created on GitHub..."
echo "   (Make sure you've created it at: https://github.com/new)"
echo ""
read -p "Press Enter once you've created the repository on GitHub..."

echo ""
echo "📤 Pushing to GitHub..."
echo ""

# Push to main branch
if git push -u origin main; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo "Repository: $REPO_URL"
else
    echo ""
    echo "❌ Push failed. Please check:"
    echo "   1. Repository exists at: $REPO_URL"
    echo "   2. You have write access"
    echo "   3. Try: git push -u origin main"
fi



