# Default target
.DEFAULT_GOAL := help

# Colors (optional, just for nicer output)
GREEN := \033[0;32m
NC := \033[0m

.PHONY: help
help: ## Show available commands
	@echo "$(GREEN)Available commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*##' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: build
build: ## Build Docker images
	docker compose build

.PHONY: up
up: ## Start services in the foreground
	docker compose up

.PHONY: up-detached
up-detached: ## Start services in detached mode
	docker compose up -d

.PHONY: down
down: ## Stop and remove containers
	docker compose down

.PHONY: logs
logs: ## Follow application logs
	docker compose logs -f app

.PHONY: migrate
migrate: ## Apply database migrations
	docker compose exec app python manage.py migrate

.PHONY: makemigrations
makemigrations: ## Create new database migrations
	docker compose exec app python manage.py makemigrations

.PHONY: test
test: ## Run tests
	docker compose exec app pytest

.PHONY: bash
bash: ## Open a bash shell in the app container
	docker compose exec app bash

.PHONY: shell
shell: ## Open a Django shell in the app container
	docker compose exec app python manage.py shell

.PHONY: db-bash
db-bash: ## Open a bash shell in the database container
	docker compose exec db bash

.PHONY: db-shell
db-shell: ## Open a psql shell in the database container
	docker compose exec db psql -U postgres
