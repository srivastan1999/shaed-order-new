#!/bin/bash

# Automated script to push to GitHub
# It will check if repo exists and push automatically

set -e

REPO_NAME="shaed-order-elt"
USERNAME="srivastan1999"
REPO_URL="https://github.com/${USERNAME}/${REPO_NAME}.git"

echo "🚀 Auto-push to GitHub"
echo "======================"
echo ""

# Set up remote
if git remote get-url origin 2>/dev/null; then
    echo "✅ Remote 'origin' exists"
    git remote set-url origin "$REPO_URL"
else
    echo "➕ Adding remote 'origin'..."
    git remote add origin "$REPO_URL"
fi

echo ""
echo "🔍 Checking if repository exists..."
echo ""

# Check if repo exists
if curl -s -o /dev/null -w "%{http_code}" "https://github.com/${USERNAME}/${REPO_NAME}" | grep -q "200"; then
    echo "✅ Repository exists!"
    echo ""
    echo "📤 Pushing code..."
    git push -u origin main
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo "Repository: $REPO_URL"
else
    echo "⚠️  Repository not found yet."
    echo ""
    echo "Please create the repository first:"
    echo "1. Go to: https://github.com/new"
    echo "2. Repository name: $REPO_NAME"
    echo "3. Make it private"
    echo "4. Don't initialize with README"
    echo ""
    echo "Then run this script again: ./auto_push.sh"
    echo ""
    echo "Or wait 10 seconds and I'll try again..."
    sleep 10
    if curl -s -o /dev/null -w "%{http_code}" "https://github.com/${USERNAME}/${REPO_NAME}" | grep -q "200"; then
        echo "✅ Repository found! Pushing..."
        git push -u origin main
        echo ""
        echo "✅ Successfully pushed!"
    else
        echo "❌ Repository still not found. Please create it manually."
    fi
fi



