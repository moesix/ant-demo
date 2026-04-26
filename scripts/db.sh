#!/bin/bash

# Database initialization script for PostgreSQL

if [ "$1" == "init" ]; then
    # Create access_logs table if it doesn't exist
    echo "Creating access_logs table if it doesn't exist..."
    PGPASSWORD=${DB_PASSWORD} psql -h ${DB_HOST} -U ${DB_USER} -d ${DB_NAME} -c "
        CREATE TABLE IF NOT EXISTS access_logs (
            id SERIAL PRIMARY KEY,
            log_message VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    "
    echo "Table created successfully"
elif [ "$1" == "seed" ]; then
    # Seed database with test data
    echo "Seeding database with test data..."
    PGPASSWORD=${DB_PASSWORD} psql -h ${DB_HOST} -U ${DB_USER} -d ${DB_NAME} -c "
        INSERT INTO access_logs (log_message) VALUES 
        ('Test log entry 1'),
        ('Test log entry 2'),
        ('Test log entry 3'),
        ('Test log entry 4'),
        ('Test log entry 5');
    "
    echo "Database seeded successfully"
elif [ "$1" == "backup" ]; then
    # Create database backup
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    FILENAME="ant-demo-backup-${TIMESTAMP}.sql"
    echo "Creating backup: ${FILENAME}"
    PGPASSWORD=${DB_PASSWORD} pg_dump -h ${DB_HOST} -U ${DB_USER} ${DB_NAME} > ${FILENAME}
    echo "Backup created successfully: ${FILENAME}"
elif [ "$1" == "restore" ]; then
    # Restore from backup
    if [ -z "$2" ]; then
        echo "Usage: $0 restore <backup_file.sql>"
        exit 1
    fi
    if [ ! -f "$2" ]; then
        echo "Backup file not found: $2"
        exit 1
    fi
    echo "Restoring database from: $2"
    PGPASSWORD=${DB_PASSWORD} psql -h ${DB_HOST} -U ${DB_USER} -d ${DB_NAME} < $2
    echo "Database restored successfully"
elif [ "$1" == "health" ]; then
    # Check database health
    echo "Checking database health..."
    if PGPASSWORD=${DB_PASSWORD} psql -h ${DB_HOST} -U ${DB_USER} -d ${DB_NAME} -c "SELECT 1" > /dev/null 2>&1; then
        echo "Database is healthy"
        exit 0
    else
        echo "Database is unhealthy"
        exit 1
    fi
else
    echo "Usage: $0 {init|seed|backup|restore|health}"
    echo "  init    - Initialize the database schema"
    echo "  seed    - Seed with test data"
    echo "  backup  - Create a database backup"
    echo "  restore - Restore from backup"
    echo "  health  - Check database health"
fi