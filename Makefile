.PHONY: help build up down restart logs ps test migrate seed shell clean docker/logs docker/build docker/up docker/down \
        docker/restart docker/test docker/migrate docker/seed docker/shell docker/clean-volumes

# Default target
.DEFAULT_GOAL := help

# Environment setup
-include env/.env
export

# Commands
DC := docker compose
PYTHON := python
PYTEST := pytest
ALEMBIC := alembic

help: ## Show this help message
	@echo 'Usage:'
	@echo '  make [target]'
	@echo ''
	@echo 'Targets:'
	@grep -E '^[a-zA-Z_/-]+:.*?## .*$$' $(MAKEFILE_LIST) | sed -E 's/^[^:]+://' | sed -E 's/^[[:space:]]+//' | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

# Development commands - local
test: ## Run tests locally
	$(PYTEST)

migrate: ## Run database migrations locally
	$(ALEMBIC) upgrade head

seed: ## Seed the database locally
	$(PYTHON) -m multiverse_market.cli seed

# Docker commands
docker/logs: ## View output from containers
	$(DC) logs -f

docker/build: ## Build or rebuild services
	$(DC) build

docker/up: ## Create and start containers
	$(DC) up -d

docker/down: ## Stop and remove containers (preserves volumes)
	$(DC) down

docker/restart: docker/down docker/up ## Restart all containers (preserves volumes)

docker/test: ## Run tests in Docker
	$(DC) exec app $(PYTEST)

docker/migrate: ## Run database migrations in Docker
	$(DC) exec app $(ALEMBIC) upgrade head

docker/seed: ## Seed the database in Docker
	$(DC) exec app $(PYTHON) -m multiverse_market.cli seed

docker/shell: ## Open a shell in the app container
	$(DC) exec app /bin/bash

docker/clean-volumes: ## Remove all volumes (WARNING: destroys data)
	$(DC) down -v