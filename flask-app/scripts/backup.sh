#!/bin/bash
# Database backup script

set -e

echo "========================================="
echo "Database Backup Script"
echo "========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
CONTAINER_NAME="ecommerce_mysql"
DATABASE_NAME="ecommerce_flask"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Check if container is running
if ! docker ps | grep -q $CONTAINER_NAME; then
    echo -e "${RED}[ERROR]${NC} Container $CONTAINER_NAME is not running!"
    exit 1
fi

# Get database credentials from environment
source .env

BACKUP_FILE="${BACKUP_DIR}/ecommerce_backup_${TIMESTAMP}.sql"

echo -e "${GREEN}[INFO]${NC} Creating backup: $BACKUP_FILE"

# Create backup
docker exec $CONTAINER_NAME mysqldump \
    -u root \
    -p${MYSQL_ROOT_PASSWORD} \
    --single-transaction \
    --routines \
    --triggers \
    --events \
    $DATABASE_NAME > $BACKUP_FILE

# Compress backup
echo -e "${GREEN}[INFO]${NC} Compressing backup..."
gzip $BACKUP_FILE

COMPRESSED_FILE="${BACKUP_FILE}.gz"

# Get file size
SIZE=$(du -h $COMPRESSED_FILE | cut -f1)

echo -e "${GREEN}[SUCCESS]${NC} Backup created: $COMPRESSED_FILE (${SIZE})"

# Delete backups older than 30 days
echo -e "${GREEN}[INFO]${NC} Cleaning old backups (older than 30 days)..."
find $BACKUP_DIR -name "ecommerce_backup_*.sql.gz" -mtime +30 -delete

# Show remaining backups
BACKUP_COUNT=$(ls -1 $BACKUP_DIR/ecommerce_backup_*.sql.gz 2>/dev/null | wc -l)
echo -e "${GREEN}[INFO]${NC} Total backups: $BACKUP_COUNT"

echo "Done!"
