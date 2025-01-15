# Dockerfile
FROM python:3.10

# On évite les *.pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Installe le client Postgres (pour pg_isready du script wait-for-postgres.sh)
RUN apt-get update && apt-get install -y postgresql-client

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Collect static, au cas où
RUN python manage.py collectstatic --noinput || true

# Rendre entrypoint.sh exécutable
RUN chmod +x /app/entrypoint.sh
RUN chmod +x /app/wait-for-postgres.sh

EXPOSE 8080

CMD ["/app/entrypoint.sh"]
