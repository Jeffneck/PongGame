#!/bin/bash
# entrypoint.sh

# Pour le debug : si tu veux voir les erreurs
set -e

echo "==> Applying migrations"
python manage.py makemigrations --noinput && echo "makemigration"
./wait-for-postgres.sh db python manage.py migrate && echo "migrate"

echo "==> Starting Daphne ASGI server on port 8080"
daphne -b 0.0.0.0 -p 8080 pong_project.asgi:application
