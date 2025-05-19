# builder stage
FROM python:3.11-slim AS builder

ENV DEBIAN_FRONTEND=no

# update packages, install gcc+libpq-dev for psycopg
RUN apt-get update && apt-get install -y gcc libpq-dev curl && \
    python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip \

COPY requirements.txt .
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# runtime image stage
FROM python:3.11-slim

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONBUFFERED=1

RUN adduser --disabled-password --no-create-home appuser
USER appuser

WORKDIR /app
COPY --chown=appuser:appuser . .

COPY --from=builder /opt/venv /opt/venv

RUN python manage.py collectstatic --noinput