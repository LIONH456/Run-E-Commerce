FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && apt-get install -y gcc default-libmysqlclient-dev build-essential libpq-dev curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/

# Create a user for safety
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

# Entrypoint will run migrations and start Gunicorn when container starts (see entrypoint.sh)
COPY compose/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
