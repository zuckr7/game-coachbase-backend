#!/bin/sh

# Ждём, пока Couchbase UI станет доступным
echo "⏳ Waiting for Couchbase cluster init..."
until curl -s -u "$USERNAME:$PASSWORD" http://couchbase:8091/pools/default | grep -q '"clusterName"'; do
  echo "  Cluster not ready - sleeping"
  sleep 5
done
echo "✅ Couchbase cluster ready!"

# Если внутри контейнера есть .env-файл, экспортируем переменные
if [ -f /django_panel/.env ]; then
  set -a
    . /django_panel/.env
  set +a
fi

# Применяем миграции
python manage.py migrate --noinput

python manage.py collectstatic --noinput

# Запускаем Gunicorn
exec gunicorn django_panel.wsgi:application \
  --bind 0.0.0.0:8001 \
  --timeout 120 \
  --workers 2