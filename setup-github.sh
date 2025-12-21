#!/bin/bash

# GitHub setup script for Planning Poker

echo "=================================================="
echo "Planning Poker - GitHub Setup"
echo "=================================================="
echo ""

# Check if gh CLI is installed
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI (gh) is installed"

    # Check if authenticated
    if gh auth status &> /dev/null; then
        echo "✅ Already authenticated with GitHub"
    else
        echo "⚠️  Not authenticated with GitHub CLI"
        echo ""
        echo "Authenticating with GitHub..."
        gh auth login
    fi

    echo ""
    read -p "Enter repository name (default: planning-poker): " REPO_NAME
    REPO_NAME=${REPO_NAME:-planning-poker}

    read -p "Make repository private? (y/N): " PRIVATE
    if [[ $PRIVATE =~ ^[Yy]$ ]]; then
        VISIBILITY="--private"
    else
        VISIBILITY="--public"
    fi

    echo ""
    echo "Creating GitHub repository: $REPO_NAME"
    gh repo create "$REPO_NAME" $VISIBILITY --source=. --push

    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Repository created and code pushed!"
        REPO_URL=$(gh repo view --json url -q .url)
        echo "   URL: $REPO_URL"

        echo ""
        echo "📝 Next steps:"
        echo "   1. Create Render account at https://render.com"
        echo "   2. Get your Render API key from Account Settings"
        echo "   3. Connect GitHub to Render (one-time setup)"
        echo "   4. Run: export RENDER_API_KEY='your-key'"
        echo "   5. Run: export GITHUB_REPO_URL='$REPO_URL'"
        echo "   6. Run: python3 deploy-render.py"
    else
        echo "❌ Failed to create repository"
        exit 1
    fi

else
    echo "⚠️  GitHub CLI (gh) not found"
    echo ""
    echo "Option 1: Install GitHub CLI (recommended)"
    echo "  macOS:   brew install gh"
    echo "  Linux:   See https://github.com/cli/cli#installation"
    echo "  Windows: See https://github.com/cli/cli#installation"
    echo ""
    echo "Then run this script again."
    echo ""
    echo "Option 2: Manual setup"
    echo "  1. Go to https://github.com/new"
    echo "  2. Create a new repository (name: planning-poker)"
    echo "  3. Run these commands:"
    echo ""
    echo "     git remote add origin https://github.com/YOUR_USERNAME/planning-poker.git"
    echo "     git branch -M main"
    echo "     git push -u origin main"
    echo ""
    exit 1
fi
