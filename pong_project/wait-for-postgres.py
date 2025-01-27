import os
import time
import psycopg2
from psycopg2 import OperationalError

def wait_for_postgres():
    # Récupérer les variables d'environnement avec des valeurs par défaut
    db_name = os.getenv('POSTGRES_DB', 'postgres')
    db_user = os.getenv('POSTGRES_USER', 'postgres')
    db_password = os.getenv('POSTGRES_PASSWORD', '')
    db_host = os.getenv('POSTGRES_HOST', 'localhost')
    db_port = os.getenv('POSTGRES_PORT', '5432')

    while True:
        try:
            print("Tentative de connexion à la base de données PostgreSQL...")
            # Établir une connexion à la base de données
            conn = psycopg2.connect(
                dbname=db_name,
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port,
            )
            conn.close()
            print("Connexion établie avec succès à la base de données PostgreSQL.")
            break
        except OperationalError as e:
            print(f"La base de données n'est pas encore prête ({e}). Nouvelle tentative dans 2 secondes...")
            time.sleep(2)

if __name__ == '__main__':
    wait_for_postgres()
