SHELL := /bin/bash
VENV_NAME := venv

all: help

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

init-prerequisites:
	./scripts/setup.sh

init: init-prerequisites
	rm -rf ${VENV_NAME}
	uv ${VENV_NAME}
	uv lock

lint:
	ruff check . --fix && ruff format .

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f


docker-logs-db:
	docker-compose logs -f postgres


docker-shell-db:
	docker-compose exec postgres /bin/bash

docker-psql:
	docker-compose exec postgres psql -U postgres -d kayrros_hotspots

docker-clean:
	docker-compose down -v
	docker-compose rm -f

.PHONY: all help clean init-prerequisites init lint docker-build docker-up docker-down \
        docker-logs  docker-logs-db docker-shell-db \
        docker-psql docker-clean
