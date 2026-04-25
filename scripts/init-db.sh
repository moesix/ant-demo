#!/bin/bash
set -e

# Create Kong database and user
echo "Creating Kong database and user..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
    CREATE USER kong WITH PASSWORD 'kongpass';
    CREATE DATABASE kong OWNER kong;
    GRANT ALL PRIVILEGES ON DATABASE kong TO kong;
EOSQL

echo "Kong database created successfully!"