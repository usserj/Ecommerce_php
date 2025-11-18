#!/bin/bash
# Deployment script for Flask E-commerce Application

set -e  # Exit on error

echo "========================================="
echo "Flask E-commerce Deployment Script"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env exists
if [ ! -f .env ]; then
    log_error ".env file not found!"
    log_info "Please create .env file from .env.example"
    exit 1
fi

# Load environment variables
source .env

# Check Docker is installed
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed!"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose is not installed!"
    exit 1
fi

log_info "Docker and Docker Compose found"

# Pull latest code (if in git repo)
if [ -d .git ]; then
    log_info "Pulling latest code from repository..."
    git pull origin main || log_warn "Failed to pull from git"
fi

# Backup database before deployment
log_info "Creating database backup..."
if docker ps | grep -q ecommerce_mysql; then
    ./scripts/backup.sh || log_warn "Backup failed"
fi

# Stop existing containers
log_info "Stopping existing containers..."
docker-compose down || true

# Remove old images (optional)
read -p "Remove old Docker images? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Removing old images..."
    docker image prune -f
fi

# Build new images
log_info "Building Docker images..."
docker-compose build --no-cache

# Run database migrations
log_info "Running database migrations..."
docker-compose run --rm app flask db upgrade || log_error "Migrations failed!"

# Start services
log_info "Starting services..."
docker-compose up -d

# Wait for services to be ready
log_info "Waiting for services to start..."
sleep 10

# Health check
log_info "Performing health check..."
for i in {1..30}; do
    if curl -f http://localhost:5000/health &> /dev/null; then
        log_info "Application is healthy!"
        break
    fi
    if [ $i -eq 30 ]; then
        log_error "Health check failed!"
        docker-compose logs app
        exit 1
    fi
    sleep 2
done

# Show running containers
log_info "Running containers:"
docker-compose ps

# Show logs
log_info "Recent logs:"
docker-compose logs --tail=50 app

echo ""
log_info "Deployment completed successfully!"
log_info "Application is running at: http://localhost"
echo ""

# Optional: Setup SSL with Certbot
read -p "Setup SSL certificate with Certbot? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Setting up SSL certificate..."
    ./scripts/setup-ssl.sh
fi

log_info "Done!"
