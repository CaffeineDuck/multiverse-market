.PHONY: help build up down restart logs ps test migrate seed shell clean docker/logs docker/build docker/up docker/down \
        docker/restart docker/test docker/migrate docker/seed docker/shell docker/clean-volumes docker/loadtest \
        docker/loadtest/logs docker/loadtest/stop docker/test/integration docker/test/integration/logs docker/test/integration/clean

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
	$(DC) exec app $(PYTHON) -m multiverse_market.cli

docker/shell: ## Open a shell in the app container
	$(DC) exec app /bin/bash

docker/clean-volumes: ## Remove all volumes (WARNING: destroys data)
	$(DC) down -v

# Load testing commands
docker/loadtest: ## Start the load testing environment
	$(DC) --profile test-load up -d

docker/loadtest/logs: ## View load testing logs
	$(DC) --profile test-load logs -f locust-master locust-worker

docker/loadtest/stop: ## Stop the load testing environment
	$(DC) --profile test-load down

# Integration testing commands
docker/test/integration: docker/test/integration/clean ## Run integration tests in Docker
	$(DC) --profile test up -d redis
	$(DC) --profile test run --rm integration-test

docker/test/integration/watch: docker/test/integration/clean ## Run integration tests in watch mode
	$(DC) --profile test up -d redis
	$(DC) --profile test run --rm integration-test pytest tests/integration -v --cov=src --cov-report=term-missing -f

docker/test/integration/logs: ## View integration test logs
	$(DC) --profile test logs -f integration-test

docker/test/integration/clean: ## Clean up integration test environment
	$(DC) --profile test down
	$(DC) --profile test rm -f integration-test