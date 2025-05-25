#!/bin/sh

# Ждём, пока Couchbase UI станет доступным
echo "Waiting for Couchbase cluster init..."
until curl -s -u "$COUCHBASE_ADMINISTRATOR_USERNAME:$COUCHBASE_ADMINISTRATOR_PASSWORD" http://couchbase:8091/pools/default | grep -q '"clusterName"'; do
  echo "  Cluster not ready - sleeping"
  sleep 5
done
echo "Couchbase cluster ready!"

# Если внутри контейнера есть .env-файл, экспортируем переменные
if [ -f /django_panel/.env ]; then
  set -a
    . /django_panel/.env
  set +a
fi

# Применяем миграции
python manage.py migrate --noinput

python manage.py collectstatic --noinput

echo "Creating superuser (if not exists)..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
import os

User = get_user_model()
username = os.getenv('USERNAME')
email = os.getenv('DJANGO_SUPERUSER_EMAIL')
password = os.getenv('PASSWORD')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superuser {username} created.")
else:
    print(f"Superuser {username} already exists.")
EOF

# Запускаем Gunicorn
exec gunicorn django_panel.wsgi:application \
  --bind 0.0.0.0:8001 \
  --timeout 120 \
  --workers 2