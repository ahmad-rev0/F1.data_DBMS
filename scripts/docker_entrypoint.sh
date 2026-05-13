#!/usr/bin/env sh
set -e
python manage.py migrate --noinput
exec gunicorn --bind "0.0.0.0:${PORT:-10000}" --workers 2 f1_platform.wsgi:application
