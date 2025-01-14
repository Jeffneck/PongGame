# Dockerfile
FROM python:3.10

# On évite les *.pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Collect static, au cas où
RUN python manage.py collectstatic --noinput || true

# Rendre entrypoint.sh exécutable
RUN chmod +x /app/entrypoint.sh

EXPOSE 8080

CMD ["/app/entrypoint.sh"]
