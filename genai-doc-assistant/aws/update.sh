#!/bin/bash
# Pull latest code and redeploy
# Run from the genai-doc-assistant directory

set -e

echo "=== Updating GenAI Document Assistant ==="

cd "$(dirname "$0")/.."

echo "Pulling latest code..."
git pull origin main

echo "Rebuilding and restarting..."
docker compose up -d --build

echo "Waiting for health check..."
sleep 10
curl -s http://localhost:80/api/health-check | python3 -m json.tool

echo ""
echo "=== Update Complete ==="
