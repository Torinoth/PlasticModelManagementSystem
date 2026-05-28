#!/bin/bash
set -e

echo "[entrypoint] Running database migrations..."
python manage.py migrate --noinput

if [ "${DEBUG}" != "True" ]; then
    echo "[entrypoint] Collecting static files..."
    python manage.py collectstatic --noinput --clear
fi

echo "[entrypoint] Starting server..."
exec "$@"
