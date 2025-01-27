# Dockerfile

FROM python:3.10

# Évite les *.pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Installe le client Postgres (pour pg_isready du script wait-for-postgres.sh)
RUN apt-get update && apt-get install -y postgresql-client

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Collecte des fichiers statiques
RUN python manage.py collectstatic --noinput || true

# Rendre les scripts exécutables
RUN chmod +x /app/entrypoint.sh
RUN chmod +x /app/wait-for-postgres.py

EXPOSE 8000

CMD ["bash", "/app/entrypoint.sh"]
