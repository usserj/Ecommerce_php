#!/bin/bash
# Database restore script

set -e

echo "========================================="
echo "Database Restore Script"
echo "========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
BACKUP_DIR="./backups"
CONTAINER_NAME="ecommerce_mysql"
DATABASE_NAME="ecommerce_flask"

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${RED}[ERROR]${NC} Backup directory not found: $BACKUP_DIR"
    exit 1
fi

# List available backups
echo -e "${GREEN}[INFO]${NC} Available backups:"
echo ""
ls -lh $BACKUP_DIR/ecommerce_backup_*.sql.gz 2>/dev/null || {
    echo -e "${RED}[ERROR]${NC} No backups found!"
    exit 1
}
echo ""

# Ask user to select backup
read -p "Enter backup filename (or 'latest' for most recent): " BACKUP_CHOICE

if [ "$BACKUP_CHOICE" = "latest" ]; then
    BACKUP_FILE=$(ls -t $BACKUP_DIR/ecommerce_backup_*.sql.gz | head -1)
else
    BACKUP_FILE="$BACKUP_DIR/$BACKUP_CHOICE"
fi

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}[ERROR]${NC} Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo -e "${GREEN}[INFO]${NC} Selected backup: $BACKUP_FILE"

# Warning
echo -e "${YELLOW}[WARNING]${NC} This will REPLACE the current database!"
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

# Load environment
source .env

# Check if container is running
if ! docker ps | grep -q $CONTAINER_NAME; then
    echo -e "${RED}[ERROR]${NC} Container $CONTAINER_NAME is not running!"
    exit 1
fi

# Decompress if needed
if [[ $BACKUP_FILE == *.gz ]]; then
    echo -e "${GREEN}[INFO]${NC} Decompressing backup..."
    gunzip -c $BACKUP_FILE > /tmp/restore_temp.sql
    SQL_FILE="/tmp/restore_temp.sql"
else
    SQL_FILE=$BACKUP_FILE
fi

# Restore database
echo -e "${GREEN}[INFO]${NC} Restoring database..."

docker exec -i $CONTAINER_NAME mysql \
    -u root \
    -p${MYSQL_ROOT_PASSWORD} \
    $DATABASE_NAME < $SQL_FILE

# Cleanup
if [ -f /tmp/restore_temp.sql ]; then
    rm /tmp/restore_temp.sql
fi

echo -e "${GREEN}[SUCCESS]${NC} Database restored successfully!"
echo ""
echo -e "${YELLOW}[INFO]${NC} Remember to restart the application:"
echo "docker-compose restart app"
