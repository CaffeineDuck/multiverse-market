.PHONY: build up down restart logs ps test migrate seed shell clean clean-all clean-volumes help \
        docker/test docker/migrate docker/seed docker/shell

# Default target
.DEFAULT_GOAL := help

# Commands
DC = docker compose
PYTHON = python
PYTEST = pytest
ALEMBIC = alembic

help: ## Show this help message
	@echo 'Usage:'
	@echo '  make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Docker management
build: ## Build or rebuild services
	$(DC) build

up: ## Create and start containers
	$(DC) up -d

down: ## Stop and remove containers (preserves volumes)
	$(DC) down

restart: down up ## Restart all containers (preserves volumes)

logs: ## View output from containers
	$(DC) logs -f

ps: ## List containers
	$(DC) ps

# Development commands - local
test: ## Run tests locally
	$(PYTEST)

docker/test: ## Run tests in Docker
	$(DC) exec app $(PYTEST)

migrate: ## Run database migrations locally
	$(ALEMBIC) upgrade head

docker/migrate: ## Run database migrations in Docker
	$(DC) exec app $(ALEMBIC) upgrade head

seed: ## Seed the database locally
	$(PYTHON) -m multiverse_market.cli seed

docker/seed: ## Seed the database in Docker
	$(DC) exec app $(PYTHON) -m multiverse_market.cli seed

shell: ## Open a local shell with environment
	@echo "Opening a local shell..."
	@/bin/bash

docker/shell: ## Open a shell in the app container
	$(DC) exec app /bin/bash

# Cleanup commands
clean: down ## Stop containers and clean cache (preserves volumes)
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache

clean-volumes: ## Remove all volumes (WARNING: destroys data)
	$(DC) down -v

clean-all: clean-volumes ## Stop containers, clean cache, and remove volumes (WARNING: destroys all data)
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache 