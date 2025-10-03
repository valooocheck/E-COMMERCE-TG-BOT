DOCKER_COMPOSE_SERVER=./docker-compose.yml
DOCKER_COMPOSE_LOCAL=./docker-compose.local.yml

build:
	docker compose -f docker-compose.yml build --force-rm

up:
	docker compose -f docker-compose.yml up -d --build --force-recreate


ruff-check:
	ruff check --fix --config=./pyproject.toml .

ruff-format:
	ruff format --config=./pyproject.toml .


build-local:
	docker compose -f $(DOCKER_COMPOSE_LOCAL) build


up-local:
	docker compose -f $(DOCKER_COMPOSE_LOCAL) up -d --build