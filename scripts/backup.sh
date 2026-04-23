#!/bin/bash

# Database backup script for Docker Compose

# Load environment variables from .env
if [ -f .env ]; then
    source .env
else
    echo "Error: .env file not found"
    exit 1
fi

# Create backup directory if it doesn't exist
mkdir -p backups

# Generate timestamp for backup filename
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="backups/ant-demo-backup-${TIMESTAMP}.sql"

# Run pg_dump on the PostgreSQL container
echo "Creating database backup: ${BACKUP_FILE}"
if docker-compose exec -T postgres_db pg_dump -U ${DB_USER} -d ${DB_NAME} > ${BACKUP_FILE}; then
    echo "Backup created successfully: ${BACKUP_FILE}"
    
    # Optional: Compress the backup
    if gzip -f ${BACKUP_FILE}; then
        echo "Backup compressed to: ${BACKUP_FILE}.gz"
    fi
else
    echo "Error: Failed to create backup"
    exit 1
fi

# Optional: Clean up old backups (keep last 7 days)
echo "Cleaning up old backups..."
find backups/ -type f -name "*.sql" -o -name "*.sql.gz" -mtime +7 -delete

echo "Backup process completed"