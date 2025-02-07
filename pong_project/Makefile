ifneq (,$(wildcard .env))
    include .env
    export
endif

ifeq ($(strip $(COMPOSE_FILE)),)
    COMPOSE_FILE=docker-compose.yml
endif

# Cibles

up:
	docker compose --env-file .env -f $(COMPOSE_FILE) up

down:
	docker compose --env-file .env -f $(COMPOSE_FILE) down

clean:
	docker compose --env-file .env -f $(COMPOSE_FILE) down --volumes --remove-orphans

build:
	docker compose --env-file .env -f $(COMPOSE_FILE) build

prune:
	docker system prune --all --force
	docker volume prune --force
	docker network prune --force

reset: clean build up
	@echo "Containers and volumes removed, images rebuilt, environment is fresh!"

re:
	docker compose --env-file .env -f $(COMPOSE_FILE) down --volumes --remove-orphans
	docker compose --env-file .env -f $(COMPOSE_FILE) up