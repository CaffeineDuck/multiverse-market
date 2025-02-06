.PHONY: build up down restart logs ps test migrate seed shell clean help

# Default target
.DEFAULT_GOAL := help

# Docker compose command
DC = docker compose

help: ## Show this help message
	@echo 'Usage:'
	@echo '  make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build or rebuild services
	$(DC) build

up: ## Create and start containers
	$(DC) up -d

down: ## Stop and remove containers
	$(DC) down

restart: down up ## Restart all containers

logs: ## View output from containers
	$(DC) logs -f

ps: ## List containers
	$(DC) ps

test: ## Run tests
	$(DC) exec app pytest

migrate: ## Run database migrations
	$(DC) exec app alembic upgrade head

seed: ## Seed the database with test data
	$(DC) exec app python -m multiverse_market.cli seed

shell: ## Open a shell in the app container
	$(DC) exec app /bin/bash

clean: down ## Stop containers and clean up
	$(DC) down -v --remove-orphans
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache 