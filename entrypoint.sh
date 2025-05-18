#!/bin/sh

# Ждём, пока Couchbase UI станет доступным
echo "⏳ Waiting for Couchbase to be ready..."
until curl -s http://couchbase:8091/pools > /dev/null; do
  echo "  Couchbase is still unavailable - sleeping"
  sleep 5
done
echo "✅ Couchbase is up!"

# Если внутри контейнера есть .env-файл, экспортируем переменные
if [ -f /django_panel/.env ]; then
  export $(grep -v '^#' /django_panel/.env | xargs)
fi

# Применяем миграции
python manage.py migrate --noinput

# Запускаем Gunicorn
exec gunicorn django_panel.wsgi:application --bind 0.0.0.0:8001
