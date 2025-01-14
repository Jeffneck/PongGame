# Dockerfile

FROM python:3.10

WORKDIR /app

# Copier requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY . /app/

# Collecte statique (si tu veux que /app/static/ soit prêt)
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Lancer daphne (ou uvicorn)
CMD ["daphne", "--bind", "0.0.0.0", "--port", "8000", "pong_project.asgi:application"]
