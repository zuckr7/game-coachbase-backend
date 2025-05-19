FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /django_panel

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./django_panel/ .

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

