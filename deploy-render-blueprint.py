#!/usr/bin/env python3
"""
Render Blueprint deployment script for Planning Poker app.
Uses render.yaml to deploy all services at once with free tier support.
"""

import os
import sys
import requests
from typing import Dict, Any

# Render API configuration
RENDER_API_BASE = "https://api.render.com/v1"


class RenderBlueprintDeployer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def _request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make API request to Render"""
        url = f"{RENDER_API_BASE}{endpoint}"
        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            json=data
        )

        if response.status_code >= 400:
            print(f"❌ API Error {response.status_code}: {response.text}")
            sys.exit(1)

        return response.json() if response.text else {}

    def get_owner_id(self) -> str:
        """Get the owner ID (user or team)"""
        print("🔍 Getting owner information...")
        data = self._request("GET", "/owners")
        if not data or len(data) == 0:
            print("❌ No owners found. Please check your API key.")
            sys.exit(1)

        owner = data[0]
        owner_id = owner.get("owner", {}).get("id")
        owner_name = owner.get("owner", {}).get("name", "Unknown")
        print(f"✅ Found owner: {owner_name} ({owner_id})")
        return owner_id

    def create_blueprint(self, owner_id: str, repo_url: str, branch: str = "main") -> Dict[str, Any]:
        """Create a blueprint instance from render.yaml in the repository"""
        print("\n🚀 Creating Blueprint deployment from render.yaml...")

        # Extract repo path from URL
        # https://github.com/username/repo -> username/repo
        repo_path = repo_url.replace("https://github.com/", "").replace(".git", "")

        data = {
            "ownerId": owner_id,
            "repo": f"https://github.com/{repo_path}",
            "branch": branch,
            "blueprintPath": "render.yaml"
        }

        print(f"   Repository: {repo_path}")
        print(f"   Branch: {branch}")
        print(f"   Blueprint: render.yaml")

        blueprint_data = self._request("POST", "/blueprints", data)

        print("\n✅ Blueprint deployment initiated!")
        return blueprint_data

    def list_blueprints(self) -> list:
        """List all blueprints"""
        print("\n📋 Listing existing blueprints...")
        blueprints = self._request("GET", "/blueprints")

        if not blueprints:
            print("   No blueprints found")
            return []

        for bp in blueprints:
            name = bp.get("name", "Unknown")
            repo = bp.get("repo", "Unknown")
            print(f"   - {name} ({repo})")

        return blueprints

    def sync_blueprint(self, blueprint_id: str):
        """Sync/update an existing blueprint"""
        print(f"\n🔄 Syncing blueprint: {blueprint_id}")
        self._request("POST", f"/blueprints/{blueprint_id}/sync", {})
        print("✅ Blueprint sync initiated!")

    def deploy(self, repo_url: str, branch: str = "main"):
        """Main deployment flow"""
        print("🚀 Starting Render Blueprint deployment for Planning Poker\n")
        print(f"Repository: {repo_url}")
        print(f"Branch: {branch}\n")

        # Get owner ID
        owner_id = self.get_owner_id()

        # Check for existing blueprints
        existing_blueprints = self.list_blueprints()

        # Look for existing blueprint with same repo
        repo_path = repo_url.replace("https://github.com/", "").replace(".git", "")
        existing_blueprint = None

        for bp in existing_blueprints:
            if repo_path in bp.get("repo", ""):
                existing_blueprint = bp
                break

        if existing_blueprint:
            blueprint_id = existing_blueprint.get("id")
            print(f"\n📌 Found existing blueprint: {blueprint_id}")
            print("   Syncing to update services...")
            self.sync_blueprint(blueprint_id)
        else:
            # Create new blueprint
            blueprint_data = self.create_blueprint(owner_id, repo_url, branch)
            blueprint_id = blueprint_data.get("id")

        print("\n" + "="*60)
        print("🎉 Deployment Initiated!")
        print("="*60)
        print(f"\n📍 Next steps:")
        print(f"   1. Go to: https://dashboard.render.com/")
        print(f"   2. Monitor your services as they deploy")
        print(f"   3. Initial build takes 5-10 minutes")
        print(f"\n💡 Your services will be created:")
        print(f"   - planning-poker-redis (Redis)")
        print(f"   - planning-poker-backend (Web Service)")
        print(f"   - planning-poker-frontend (Static Site)")
        print(f"\n⏳ Builds are happening now. Check dashboard for URLs once complete.")


def main():
    print("Planning Poker - Render Blueprint Deployment")
    print("=" * 60 + "\n")

    # Get API key
    api_key = os.getenv("RENDER_API_KEY")
    if not api_key:
        print("❌ Error: RENDER_API_KEY environment variable not set")
        print("\nTo get your API key:")
        print("1. Go to https://dashboard.render.com/")
        print("2. Navigate to Account Settings → API Keys")
        print("3. Create a new API key")
        print("4. Set it as: export RENDER_API_KEY='your-key-here'")
        sys.exit(1)

    # Get repository URL
    repo_url = os.getenv("GITHUB_REPO_URL")
    if not repo_url:
        print("❌ Error: GITHUB_REPO_URL environment variable not set")
        print("\nSet your GitHub repository URL:")
        print("export GITHUB_REPO_URL='https://github.com/yourusername/planning-poker'")
        sys.exit(1)

    # Validate repo format
    if not repo_url.startswith("https://github.com/"):
        print("❌ Error: Repository URL must be in format: https://github.com/username/repo")
        sys.exit(1)

    # Get optional branch
    branch = os.getenv("GITHUB_BRANCH", "main")

    # Deploy
    deployer = RenderBlueprintDeployer(api_key)
    deployer.deploy(repo_url, branch)


if __name__ == "__main__":
    main()
