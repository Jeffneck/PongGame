#!/bin/bash
# entrypoint.sh

# Pour le debug : si tu veux voir les erreurs
set -e

echo "==> Applying migrations"
python manage.py makemigrations
python manage.py migrate

echo "==> Starting game loop in background"
python manage.py run_game_loop &

echo "==> Starting Daphne ASGI server on port 8080"
daphne -b 0.0.0.0 -p 8080 pong_project.asgi:application
