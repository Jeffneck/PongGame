#!/bin/bash
# entrypoint.sh

set -e

echo "==> Waiting for postgreSQL"
python wait-for-postgres.py
echo "==> Applying migrations"
python manage.py makemigrations
python manage.py migrate

echo "==> Collecting static files"
python manage.py collectstatic --noinput

echo "==> Starting Uvicorn ASGI server"
# Utilisez exec pour que le processus Uvicorn remplace le processus shell, ce qui facilite la gestion des signaux et des arrêts propres.
exec uvicorn pong_project.asgi:application --host 0.0.0.0 --port 8000
