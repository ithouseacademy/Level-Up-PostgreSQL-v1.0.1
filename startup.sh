#!/bin/bash
set -e

echo "Migrating database..."
python manage.py migrate --noinput
python manage.py createcachetable --noinput 2>/dev/null || true

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Creating superuser if not exists..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
import os
User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superuser \"{username}\" created')
else:
    print(f'Superuser \"{username}\" already exists')
"

echo "Starting gunicorn..."
exec gunicorn myadminproject.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 4 --timeout 120
