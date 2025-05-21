#!/usr/bin/env bash
set -euo pipefail

CB_USER="${COUCHBASE_ADMINISTRATOR_USERNAME}"
CB_PASS="${COUCHBASE_ADMINISTRATOR_PASSWORD}"
COUCH_HOST="0.0.0.0"  # Явное указание интерфейса

# 1) Старт Couchbase в фоне
/opt/couchbase/bin/couchbase-server -- -noinput & CB_PID=$!

# 2) Ждём REST API
echo "⏳ Waiting for Couchbase REST API..."
until curl -sI "http://${COUCH_HOST}:8091/pools" | grep -q "200 OK"; do
  sleep 2
done
echo "Couchbase REST API ready!"

# 3) Инициализация кластера
if ! couchbase-cli cluster-list -c "$COUCH_HOST" -u "$CB_USER" -p "$CB_PASS" &>/dev/null; then
  echo "⚙️ Initializing cluster..."
  couchbase-cli cluster-init -c "$COUCH_HOST" \
    --cluster-username "$CB_USER" \
    --cluster-password "$CB_PASS" \
    --services data,index,query \
    --cluster-ramsize 512
else
  echo "Cluster already initialized"
fi

# 4) Создание бакетов
for bucket in players_db levels_db; do
  if ! couchbase-cli bucket-list -c "$COUCH_HOST" -u "$CB_USER" -p "$CB_PASS" | grep -q "\"$bucket\""; then
    echo "⚙️ Creating bucket: $bucket"
    couchbase-cli bucket-create -c "$COUCH_HOST" \
      -u "$CB_USER" -p "$CB_PASS" \
      --bucket "$bucket" \
      --bucket-type couchbase \
      --bucket-ramsize 128
  else
    echo "Bucket $bucket exists"
  fi
done

# 5) Индексы
echo "⚙️ Creating primary indexes..."
for bucket in players_db levels_db; do
  until /opt/couchbase/bin/cbq -e "http://$COUCH_HOST:8093" -u "$CB_USER" -p "$CB_PASS" \
    --script "CREATE PRIMARY INDEX IF NOT EXISTS ON \`$bucket\`"; do
    echo "Retrying index creation for $bucket..."
    sleep 2
  done
done

# 6) Бесконечное ожидание для healthcheck
echo "✅ Couchbase initialization complete"
wait $CB_PID
