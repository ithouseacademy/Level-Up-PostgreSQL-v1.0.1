Write-Host "Migrating database..." -ForegroundColor Green
python manage.py migrate --noinput

Write-Host "Collecting static files..." -ForegroundColor Green
python manage.py collectstatic --noinput --clear

Write-Host "Creating superuser if not exists..." -ForegroundColor Green
$username = [System.Environment]::GetEnvironmentVariable("DJANGO_SUPERUSER_USERNAME", "User")
$email = [System.Environment]::GetEnvironmentVariable("DJANGO_SUPERUSER_EMAIL", "User")
$password = [System.Environment]::GetEnvironmentVariable("DJANGO_SUPERUSER_PASSWORD", "User")
if (-not $username) { $username = "admin" }
if (-not $email) { $email = "admin@example.com" }
if (-not $password) { $password = "admin123" }

python manage.py shell -c @"
from django.contrib.auth import get_user_model
import os
User = get_user_model()
username = '$username'
email = '$email'
password = '$password'
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superuser \"{username}\" created')
else:
    print(f'Superuser \"{username}\" already exists')
"@

Write-Host "Starting gunicorn..." -ForegroundColor Green
$port = if ([System.Environment]::GetEnvironmentVariable("PORT")) { [System.Environment]::GetEnvironmentVariable("PORT") } else { "8000" }
gunicorn myadminproject.wsgi:application --bind 0.0.0.0:$port --workers 4 --timeout 120
