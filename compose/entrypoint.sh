#!/bin/sh
set -e

# wait for DB
if [ -n "$DB_HOST" ]; then
  echo "Waiting for DB ($DB_HOST)..."
  until nc -z $DB_HOST $DB_PORT; do
    sleep 1
  done
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Start Gunicorn
exec gunicorn minishop.wsgi:application --bind 0.0.0.0:8000 --workers 3
