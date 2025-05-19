FROM couchbase:community-7.1.1

RUN apt-get update && \
    apt-get install -y curl jq && \
    rm -rf /var/lib/apt/lists/*

COPY init-couchbase.sh /init-couchbase.sh
RUN chmod +x /init-couchbase.sh

ENTRYPOINT ["/init-couchbase.sh"]
