import os
import sys
import subprocess
import time
import psycopg2
from psycopg2 import OperationalError

def wait_for_postgres(host, user, password, db_name, port=5432):
    """
    Attendre que PostgreSQL soit prêt avant de continuer.
    """
    while True:
        try:
            print(f"==> Tentative de connexion à PostgreSQL ({host}:{port})...")
            conn = psycopg2.connect(
                dbname=db_name,
                user=user,
                password=password,
                host=host,
                port=port,
            )
            conn.close()
            print("==> PostgreSQL est prêt.")
            break
        except OperationalError as e:
            print(f"==> PostgreSQL n'est pas prêt : {e}")
            print("==> Nouvelle tentative dans 2 secondes...")
            time.sleep(2)

def run_command(command):
    """
    Exécute une commande système et affiche sa sortie.
    """
    print(f"==> Exécution : {' '.join(command)}")
    result = subprocess.run(command, check=True, text=True)
    return result.returncode

def main():
    # Récupération des variables d'environnement
    postgres_host = os.getenv('POSTGRES_HOST', 'db')
    postgres_user = os.getenv('POSTGRES_USER', 'postgres')
    postgres_password = os.getenv('POSTGRES_PASSWORD', 'postgres')
    postgres_db = os.getenv('POSTGRES_DB', 'pong_db')
    postgres_port = os.getenv('POSTGRES_PORT', '5432')

    # Attendre que PostgreSQL soit prêt
    wait_for_postgres(postgres_host, postgres_user, postgres_password, postgres_db, postgres_port)

    # Appliquer les migrations
    print("==> Applying migrations")
    run_command(['python', 'manage.py', 'makemigrations', 'game', '--noinput'])
    run_command(['python', 'manage.py', 'migrate'])

    # Collecter les fichiers statiques
    print("==> Collecting static files")
    run_command(['python', 'manage.py', 'collectstatic', '--noinput'])

    # Démarrer le serveur Uvicorn
    print("==> Starting Uvicorn ASGI server")
    run_command(['uvicorn', 'pong_project.asgi:application', '--host', '0.0.0.0', '--port', '8000'])

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"==> Une erreur est survenue : {e}", file=sys.stderr)
        sys.exit(1)
