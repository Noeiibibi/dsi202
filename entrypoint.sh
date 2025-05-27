#!/bin/bash
set -e 
echo "Waiting for PostgreSQL database to be ready..."
while ! pg_isready -h db -p 5432 -U your_db_user; do
  echo "Database is not ready yet. Retrying in 1 second..."
  sleep 1
done
echo "PostgreSQL database is ready!"

python manage.py migrate --noinput

echo "Starting Django development server..."
exec python manage.py runserver 0.0.0.0:8000

