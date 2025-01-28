#!/bin/bash
# entrypoint.sh

# Pour le debug : si tu veux voir les erreurs
set -e

echo "==> Waiting for postgreSQL"
python wait-for-postgres.py
echo "==> Applying migrations"
python manage.py makemigrations
python manage.py migrate

# echo "==> Starting Daphne ASGI server on port 8080"
# daphne -b 0.0.0.0 -p 8080 pong_project.asgi:application
echo "==> Starting Uvicorn ASGI server on port 8080"
uvicorn pong_project.asgi:application --host 0.0.0.0 --port 8080
