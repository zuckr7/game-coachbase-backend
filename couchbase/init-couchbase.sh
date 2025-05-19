#!/usr/bin/env bash
set -euo pipefail

CB_USER="${COUCHBASE_ADMINISTRATOR_USERNAME}"
CB_PASS="${COUCHBASE_ADMINISTRATOR_PASSWORD}"
COUCH_HOST="${COUCH_HOST:-127.0.0.1}"

# 1) Старт Couchbase
/entrypoint.sh couchbase-server & CB_PID=$!

# 2) Ждём REST API
until curl -sI "http://$COUCH_HOST:8091/pools" | grep -q "200 OK"; do
  echo "Waiting for Couchbase…"
  sleep 5
done
echo "Couchbase is up!"

# 3) cluster-init (один раз)
couchbase-cli cluster-init -c "$COUCH_HOST" \
  --cluster-username "$CB_USER" \
  --cluster-password "$CB_PASS" \
  --services data,index,query \
  --cluster-ramsize 512 \
  || echo "Cluster already initialized"

# 4) Создание бакетов
for bucket in players_db levels_db; do
  if ! couchbase-cli bucket-list -c "$COUCH_HOST" \
       -u "$CB_USER" -p "$CB_PASS" \
     | grep -q "\"name\": *\"$bucket\""; then
    echo "Creating bucket $bucket"
    couchbase-cli bucket-create -c "$COUCH_HOST" \
      -u "$CB_USER" -p "$CB_PASS" \
      --bucket "$bucket" \
      --bucket-type couchbase \
      --bucket-ramsize 128
  else
    echo "Bucket $bucket already exists, skipping"
  fi
done

# 4.5) Создаём PRIMARY INDEX через cbq
for bucket in players_db levels_db; do
  echo "Ensuring primary index on \`$bucket\`..."
  /opt/couchbase/bin/cbq \
    -e "http://$COUCH_HOST:8093" \
    -u "$CB_USER" -p "$CB_PASS" \
    -s "CREATE PRIMARY INDEX IF NOT EXISTS ON \`$bucket\`;"
done

# 5) Фореґраунд
wait "$CB_PID"
