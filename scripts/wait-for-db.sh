#!/bin/bash

# Docker Compose health check script for PostgreSQL

# Maximum wait time in seconds
MAX_WAIT=60
# Wait interval in seconds
WAIT_INTERVAL=5

echo "Waiting for PostgreSQL database to become available..."

for (( i=0; i<MAX_WAIT; i+=WAIT_INTERVAL )); do
    if docker-compose exec -T postgres_db pg_isready -U ${DB_USER} -d ${DB_NAME} > /dev/null 2>&1; then
        echo "PostgreSQL database is available!"
        # Initialize database schema
        echo "Initializing database schema..."
        docker-compose exec -T webapp /bin/sh -c "
            export DB_HOST=postgres_db
            export DB_USER=${DB_USER}
            export DB_PASSWORD=${DB_PASSWORD}
            export DB_NAME=${DB_NAME}
            /app/scripts/db.sh init
        "
        echo "Database initialization complete"
        exit 0
    fi
    echo "Database not ready yet, waiting ${WAIT_INTERVAL} seconds..."
    sleep ${WAIT_INTERVAL}
done

echo "Timeout waiting for PostgreSQL database"
exit 1