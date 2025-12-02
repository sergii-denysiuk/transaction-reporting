# Default target
.DEFAULT_GOAL := help

# Colors (optional, just for nicer output)
GREEN := \033[0;32m
NC := \033[0m

VENV_DIR := .venv
PYTHON   := python3

.PHONY: help
help: ## Show available commands
	@echo "$(GREEN)Available commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*##' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: build
build: ## Build Docker images
	docker compose build

.PHONY: up
up: build ## Start services in the foreground
	docker compose up

.PHONY: up-detached
up-detached: build ## Start services in detached mode
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

.PHONY: bash
bash: ## Open a bash shell in the app container
	docker compose exec app bash

.PHONY: bash-admin
bash-admin: ## Open a bash shell in the app container as the admin user
	docker compose exec -u 0:0 app bash

.PHONY: shell
shell: ## Open a Django shell in the app container
	docker compose exec app python manage.py shell

.PHONY: db-bash
db-bash: ## Open a bash shell in the database container
	docker compose exec db bash

.PHONY: db-shell
db-shell: ## Open a psql shell in the database container
	docker compose exec db psql -U postgres

.PHONY: test
test: ## Run tests
	docker compose run --rm app pytest

# Dependency management strictly via Docker (Poetry inside container)
.PHONY: poetry-add
poetry-add: ## Add a new dependency via Poetry in Docker. Usage: make poetry-add ARGS="<package>"
	docker compose run --rm -u 0:0 app poetry add $(ARGS)

.PHONY: poetry-update
poetry-update: ## Update dependencies via Docker
	docker compose run --rm -u 0:0 app poetry update

.PHONY: poetry-lock
poetry-lock: ## Regenerate poetry.lock via Docker
	docker compose run --rm -u 0:0 app poetry lock

.PHONY: dev-setup
dev-setup: ## Create venv and install pre-commit + hooks
	@test -d $(VENV_DIR) || $(PYTHON) -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/python -m pip install --upgrade pip pre-commit
	$(VENV_DIR)/bin/pre-commit install --install-hooks

.PHONY: hooks-update-and-commit
hooks-update-and-commit: ## Autoupdate hook versions
	$(VENV_DIR)/bin/pre-commit autoupdate
	git add .pre-commit-config.yaml
	git commit -m "chore: pre-commit autoupdate"

.PHONY: qa
qa: ## Run all pre-commit hooks against all files
	$(VENV_DIR)/bin/pre-commit run --all-files

.PHONY: format
format: ## Apply formatting and autofixes
	$(VENV_DIR)/bin/pre-commit run black --all-files
	$(VENV_DIR)/bin/pre-commit run isort --all-files
	$(VENV_DIR)/bin/pre-commit run ruff --all-files

.PHONY: typecheck
typecheck: ## Run mypy type checking
	$(VENV_DIR)/bin/pre-commit run mypy --all-files
