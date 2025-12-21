#!/usr/bin/env python3
"""
Render deployment script for Planning Poker app.
Uses the Render API to deploy services defined in render.yaml.
"""

import os
import sys
import requests
from typing import Dict, Any, Optional

# Render API configuration
RENDER_API_BASE = "https://api.render.com/v1"


class RenderDeployer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None, allow_404: bool = False) -> Dict[str, Any]:
        """Make API request to Render"""
        url = f"{RENDER_API_BASE}{endpoint}"
        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            json=data
        )

        if response.status_code >= 400:
            if allow_404 and response.status_code == 404:
                return {}
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

    def find_service_by_name(self, name: str, service_type: str) -> Optional[Dict[str, Any]]:
        """Find a service by name and type"""
        services = self._request("GET", "/services")

        for service_item in services:
            service = service_item.get("service", {})
            if service.get("name") == name and service.get("type") == service_type:
                return service

        return None

    def find_redis_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find Redis instance by name"""
        redis_list = self._request("GET", "/redis")

        for redis_item in redis_list:
            if redis_item.get("name") == name:
                return redis_item

        return None

    def create_redis(self, owner_id: str) -> Dict[str, Any]:
        """Create or get existing Redis instance"""
        name = "planning-poker-redis"

        # Check if Redis already exists
        print(f"\n📦 Checking for existing Redis instance: {name}")
        existing_redis = self.find_redis_by_name(name)

        if existing_redis:
            redis_id = existing_redis.get("id")
            redis_url = existing_redis.get("connectionInfo", {}).get("internalConnectionString")
            print(f"✅ Using existing Redis: {redis_id}")
            print(f"   URL: {redis_url}")
            return existing_redis

        # Create new Redis instance
        print(f"📦 Creating new Redis instance: {name}")
        data = {
            "name": name,
            "plan": "free",
            "maxmemoryPolicy": "allkeys-lru",
            "ownerId": owner_id
        }

        redis_data = self._request("POST", "/redis", data)
        redis_id = redis_data.get("id")
        redis_url = redis_data.get("connectionInfo", {}).get("internalConnectionString")

        print(f"✅ Redis created: {redis_id}")
        print(f"   URL: {redis_url}")
        return redis_data

    def create_backend(self, owner_id: str, repo_url: str, redis_url: str, frontend_url: Optional[str] = None) -> Dict[str, Any]:
        """Create or get existing backend web service"""
        name = "planning-poker-backend"

        # Check if backend already exists
        print(f"\n🚀 Checking for existing backend service: {name}")
        existing_service = self.find_service_by_name(name, "web_service")

        if existing_service:
            backend_url = existing_service.get("serviceDetails", {}).get("url")
            print(f"✅ Using existing backend service")
            print(f"   URL: https://{backend_url}")
            return {"service": existing_service}

        # Create new backend service
        print(f"🚀 Creating new backend service: {name}")
        cors_origins = f"https://{frontend_url}" if frontend_url else "http://localhost:5173"

        data = {
            "type": "web_service",
            "name": name,
            "ownerId": owner_id,
            "repo": repo_url,
            "autoDeploy": "yes",
            "serviceDetails": {
                "env": "python",
                "plan": "free",
                "buildCommand": "pip install -r requirements.txt",
                "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
                "healthCheckPath": "/health",
                "envVars": [
                    {"key": "REDIS_URL", "value": redis_url},
                    {"key": "ENVIRONMENT", "value": "production"},
                    {"key": "LOG_LEVEL", "value": "INFO"},
                    {"key": "CORS_ORIGINS", "value": cors_origins}
                ]
            },
            "rootDir": "backend"
        }

        backend_data = self._request("POST", "/services", data)
        backend_url = backend_data.get("service", {}).get("serviceDetails", {}).get("url")

        print(f"✅ Backend created!")
        print(f"   URL: https://{backend_url}")
        return backend_data

    def create_frontend(self, owner_id: str, repo_url: str, backend_url: str) -> Dict[str, Any]:
        """Create or get existing frontend static site"""
        name = "planning-poker-frontend"

        # Check if frontend already exists
        print(f"\n🎨 Checking for existing frontend service: {name}")
        existing_service = self.find_service_by_name(name, "static_site")

        if existing_service:
            frontend_url = existing_service.get("serviceDetails", {}).get("url")
            print(f"✅ Using existing frontend service")
            print(f"   URL: https://{frontend_url}")
            return {"service": existing_service}

        # Create new frontend service
        print(f"🎨 Creating new frontend service: {name}")
        data = {
            "type": "static_site",
            "name": name,
            "ownerId": owner_id,
            "repo": repo_url,
            "autoDeploy": "yes",
            "serviceDetails": {
                "buildCommand": "npm install && npm run build",
                "publishPath": "dist",
                "envVars": [
                    {"key": "VITE_WS_URL", "value": f"https://{backend_url}"},
                    {"key": "VITE_API_URL", "value": f"https://{backend_url}"}
                ],
                "headers": [
                    {
                        "path": "/*",
                        "name": "Cache-Control",
                        "value": "public, max-age=0, must-revalidate"
                    },
                    {
                        "path": "/assets/*",
                        "name": "Cache-Control",
                        "value": "public, max-age=31536000, immutable"
                    }
                ]
            },
            "rootDir": "frontend"
        }

        frontend_data = self._request("POST", "/services", data)
        frontend_url = frontend_data.get("service", {}).get("serviceDetails", {}).get("url")

        print(f"✅ Frontend created!")
        print(f"   URL: https://{frontend_url}")
        return frontend_data

    def update_backend_cors(self, service_id: str, frontend_url: str):
        """Update backend CORS settings with frontend URL"""
        print(f"\n🔄 Updating backend CORS to allow {frontend_url}...")

        data = {
            "serviceDetails": {
                "envVars": [
                    {"key": "CORS_ORIGINS", "value": f"https://{frontend_url}"}
                ]
            }
        }

        self._request("PATCH", f"/services/{service_id}", data)
        print("✅ CORS settings updated!")

    def deploy(self, repo_url: str):
        """Main deployment flow"""
        print("🚀 Starting Render deployment for Planning Poker\n")
        print(f"Repository: {repo_url}\n")

        # Get owner ID
        owner_id = self.get_owner_id()

        # Create Redis
        redis_data = self.create_redis(owner_id)
        redis_url = redis_data.get("connectionInfo", {}).get("internalConnectionString")

        # Create backend (with placeholder CORS)
        backend_data = self.create_backend(owner_id, repo_url, redis_url)
        backend_url = backend_data.get("service", {}).get("serviceDetails", {}).get("url")
        backend_id = backend_data.get("service", {}).get("id")

        # Create frontend
        frontend_data = self.create_frontend(owner_id, repo_url, backend_url)
        frontend_url = frontend_data.get("service", {}).get("serviceDetails", {}).get("url")

        # Update backend CORS with actual frontend URL
        self.update_backend_cors(backend_id, frontend_url)

        print("\n" + "="*60)
        print("🎉 Deployment Complete!")
        print("="*60)
        print(f"\n📍 Your app URLs:")
        print(f"   Frontend: https://{frontend_url}")
        print(f"   Backend:  https://{backend_url}")
        print(f"\n⏳ Note: Initial deployment may take 5-10 minutes to build.")
        print(f"   Check status at: https://dashboard.render.com/")


def main():
    print("Planning Poker - Render Deployment Script")
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

    # Deploy
    deployer = RenderDeployer(api_key)
    deployer.deploy(repo_url)


if __name__ == "__main__":
    main()
