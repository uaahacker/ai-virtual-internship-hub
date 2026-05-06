#!/bin/bash
set -e

echo "========================================="
echo "  VIHub Backend Starting..."
echo "========================================="

echo "⏳ Waiting for PostgreSQL at $DB_HOST:$DB_PORT ..."
until nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.5
done
echo "✅ PostgreSQL is ready"

echo "📦 Applying database migrations..."
python manage.py migrate --noinput

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "📂 Ensuring media directories exist..."
mkdir -p /app/media/profile_pictures
chmod -R 755 /app/media

echo "🚀 Starting Gunicorn (workers=3, timeout=120s)..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
