#!/bin/bash
# SSL Certificate Setup with Let's Encrypt

set -e

echo "========================================="
echo "SSL Certificate Setup (Let's Encrypt)"
echo "========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if domain is provided
if [ -z "$1" ]; then
    echo -e "${RED}[ERROR]${NC} Domain not provided!"
    echo "Usage: $0 <domain> <email>"
    echo "Example: $0 example.com admin@example.com"
    exit 1
fi

if [ -z "$2" ]; then
    echo -e "${RED}[ERROR]${NC} Email not provided!"
    echo "Usage: $0 <domain> <email>"
    exit 1
fi

DOMAIN=$1
EMAIL=$2

echo -e "${GREEN}[INFO]${NC} Domain: $DOMAIN"
echo -e "${GREEN}[INFO]${NC} Email: $EMAIL"
echo ""

# Confirm
read -p "Continue with SSL setup? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "SSL setup cancelled."
    exit 0
fi

# Create directories
mkdir -p certbot/conf
mkdir -p certbot/www

# Update nginx config with domain
echo -e "${GREEN}[INFO]${NC} Updating nginx configuration..."
sed -i "s/your-domain.com/$DOMAIN/g" nginx/conf.d/app.conf

# Restart nginx
echo -e "${GREEN}[INFO]${NC} Restarting nginx..."
docker-compose restart nginx

# Request certificate
echo -e "${GREEN}[INFO]${NC} Requesting SSL certificate..."

docker-compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

# Restart nginx to apply SSL
echo -e "${GREEN}[INFO]${NC} Restarting nginx with SSL..."
docker-compose restart nginx

# Test SSL
sleep 5
echo -e "${GREEN}[INFO]${NC} Testing SSL configuration..."

if curl -sf https://$DOMAIN/health > /dev/null; then
    echo -e "${GREEN}[SUCCESS]${NC} SSL certificate installed successfully!"
    echo -e "${GREEN}[INFO]${NC} Your site is now available at: https://$DOMAIN"
else
    echo -e "${YELLOW}[WARN]${NC} SSL test failed. Please check nginx logs:"
    docker-compose logs nginx
fi

# Setup auto-renewal
echo ""
echo -e "${GREEN}[INFO]${NC} SSL certificates will auto-renew via Certbot container"
echo -e "${YELLOW}[INFO]${NC} Make sure the certbot service is running:"
echo "docker-compose ps certbot"
