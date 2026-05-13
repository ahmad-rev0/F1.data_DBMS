FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV DJANGO_SECRET_KEY=collectstatic-build-placeholder
RUN python manage.py collectstatic --noinput

RUN chmod +x /app/scripts/docker_entrypoint.sh

ENV PORT=10000
EXPOSE 10000

ENTRYPOINT ["/app/scripts/docker_entrypoint.sh"]
