# Nom du projet (optionnel si tu veux l'utiliser en variable)
PROJECT_NAME = pong_project

# Fichier docker-compose (si besoin d'un chemin particulier)
COMPOSE_FILE = docker-compose.yml

# Par défaut, on peut définir une cible "up"
up:
	docker compose -f $(COMPOSE_FILE) up 

# Stopper et supprimer les conteneurs, réseaux et volumes
down:
	docker compose -f $(COMPOSE_FILE) down

# Stopper et supprimer conteneurs + volumes + orphelins
clean:
	docker compose -f $(COMPOSE_FILE) down --volumes --remove-orphans

# Reconstruire les images
build:
	docker compose -f $(COMPOSE_FILE) build

# Nettoyer davantage (images dangling, etc.)
prune:
	docker system prune --all --force
	docker volume prune --force
	docker network prune --force

# Exemple : tout refaire (clean + build + up)
reset: clean build up
	@echo "Containers and volumes removed, images rebuilt, environment is fresh!"

# Shortcut : on peut remettre "docker compose down" si on veut juste effacer vite
re:
	docker compose -f $(COMPOSE_FILE) down --volumes --remove-orphans
	docker compose -f $(COMPOSE_FILE) up 
