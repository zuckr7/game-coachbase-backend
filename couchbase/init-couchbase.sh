#!/usr/bin/env bash
set -e

# 0) Экспорт переменных из окружения
export CB_USER="${COUCHBASE_ADMINISTRATOR_USERNAME}"
export CB_PASS="${COUCHBASE_ADMINISTRATOR_PASSWORD}"
COUCH_HOST="127.0.0.1"

# 1) Запускаем оригинальный entrypoint, он поднимет couchbase-server
/entrypoint.sh couchbase-server &
CB_PID=$!

# 2) Ждём, пока REST API станет доступно
until curl -sI http://$COUCH_HOST:8091/pools | grep -q "200 OK"; do
  echo "Waiting for Couchbase to come up…"
  sleep 5
done
echo "Couchbase is up!"

# 3) Инициализируем кластер (если ещё не инициализирован)
couchbase-cli cluster-init -c $COUCH_HOST \
  --cluster-username="$CB_USER" \
  --cluster-password="$CB_PASS" \
  --services=data,index,query \
  --cluster-ramsize=512 \
  || echo "Cluster already initialized"

# 4) Создаём бакеты, если их нет
for bucket in players_db levels_db; do
  if ! couchbase-cli bucket-list -c $COUCH_HOST \
       -u "$CB_USER" -p "$CB_PASS" \
     | grep -q "\"name\": *\"$bucket\""; then
    echo "Creating bucket $bucket"
    couchbase-cli bucket-create -c $COUCH_HOST \
      -u "$CB_USER" -p "$CB_PASS" \
      --bucket="$bucket" \
      --bucket-type=couchbase \
      --bucket-ramsize=128
  else
    echo "Bucket $bucket already exists, skipping"
  fi
done

# 5) Ожидаем Couchbase-сервер в foreground
wait $CB_PID
