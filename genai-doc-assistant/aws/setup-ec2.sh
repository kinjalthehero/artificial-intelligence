#!/bin/bash
# GenAI Document Assistant - EC2 Setup Script
# Run this on a fresh Amazon Linux 2023 or Ubuntu 22.04 EC2 instance
# Usage: bash setup-ec2.sh

set -e

echo "=== GenAI Document Assistant - EC2 Setup ==="

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
fi

# Install Docker
echo "Installing Docker..."
if [ "$OS" = "amzn" ]; then
    sudo yum update -y
    sudo yum install -y docker git
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
else
    sudo apt-get update
    sudo apt-get install -y docker.io docker-compose-plugin git
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
fi

# Install Docker Compose (if not already available)
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Installing Docker Compose..."
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep tag_name | cut -d'"' -f4)
    sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Clone the repository
echo "Cloning repository..."
if [ ! -d "artificial-intelligence" ]; then
    git clone https://github.com/kinjalthehero/artificial-intelligence.git
fi

cd artificial-intelligence/genai-doc-assistant

# Create .env file
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Edit .env and add your GOOGLE_API_KEY"
    echo "Run: nano .env"
    echo ""
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "  1. Edit .env:  nano .env  (add your GOOGLE_API_KEY)"
echo "  2. Log out and back in (for docker group permissions)"
echo "  3. Build and start:  docker compose up -d --build"
echo "  4. Check status:  docker compose ps"
echo "  5. View logs:  docker compose logs -f"
echo ""
echo "Your app will be available at http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo '<your-ec2-public-ip>'):80"
