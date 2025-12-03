# Transaction Reporting Backend

APIs for retrieving and aggregating transaction data.


## Requirements

Tools required on the host machine:
- Docker
- Docker Compose
- Python 3.* (only to create `.venv` for `pre-commit`)

Inside Docker the app uses:
- Python 3.13
- Django 5.x
- PostgreSQL 18
- Poetry 2.2


## Environment Overview

All application code, dependencies, and tests run inside Docker.
The only exception is `pre-commit` and QA tooling, which run on the host in `.venv`.

The `.venv` is created automatically by `make dev-setup` and is then used by `Makefile` targets
to run QA commands on the host (e.g. `make qa`, `make format`, `make typecheck`).

In short:
> **Host = pre-commit + QA tooling.  Docker = app, tests, and database.**

This keeps runtime/tests reproducible while keeping git hooks fast and host setup minimal.


## Project Structure
```
transaction-reporting/
├── envs/
│   ├── .env.example        # Template env. file
│   └── .env                # Actual env. variables (ignored by git)
├── transaction_reporting/  # Django project configuration
├── transactions/           # Transactions app
├── .pre-commit-config.yaml
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── pyproject.toml
└── README.md
```


## Environment Variables

Environment variables are stored in `envs/.env`.
Create this file before running the project:
```bash
cp envs/.env.example envs/.env
```


## First-Time Setup

Run these steps once when you start working on the project.

1. Create the environment file:
   ```bash
   cp envs/.env.example envs/.env
   ```
2. Setup development environment (pre-commit, etc):
   ```bash
   make dev-setup
   ```
3. Build and start the application:
   ```bash
   make build
   make up
   ```
4. Run database migrations:
   ```bash
   make migrate
   ```
5. (Optional) Create a superuser
   ```bash
   make bash
   python manage.py createsuperuser
   ```

The server is available at: http://localhost:8000


## Sample Data / Seeding

To load sample transaction data into the database, a custom management command
reads from a JSON fixture and performs validation plus bulk insert.

Fixture path (default): `transactions/fixtures/transactions.json`

Run the command inside Docker:
```bash
docker compose exec app python manage.py load_transactions
```

Optionally, you can point it at a different JSON file:
```bash
docker compose exec app python manage.py load_transactions --path /app/path/to/your.json
```


## Development

### Running the Application

The backend runs entirely inside Docker. Typical commands:
```bash
make build            # Build images
make up               # Start services
make up-detached      # Start in background
make down             # Stop containers
make logs             # View app logs
```

### Migrations
```bash
make migrate
make makemigrations
```

### Shells
```bash
make bash             # Shell inside app container
make bash-admin       # Shell as root
make shell            # Django shell
make db-bash          # Shell inside DB container
make db-shell         # psql shell
```

### Dependency Management (Poetry in Docker)

Poetry is installed inside the Docker image and is used for all dependency management.

Add a dependency:
```bash
make poetry-add ARGS="<package>"
```
Update dependencies:
```bash
make poetry-update
```
Regenerate poetry.lock:
```bash
make poetry-lock
```

These commands run Poetry inside Docker using -u 0:0 to avoid certificate issues in slim images.

### Code Quality & Pre-commit Hooks

`pre-commit` runs on the host in a local virtualenv (.venv).
It enforces: black (formatting), isort (imports), ruff (linting and autofix), mypy (typing), etc.

Install once:
```bash
make dev-setup
```

Run checks manually:
```bash
make qa
```
Format code:
```bash
make format
```
Run typing checks:
```bash
make typecheck
```

Git hooks run automatically on every commit.

### Testing

Tests run inside Docker to ensure a reproducible environment:
```bash
make test
```
This uses the same dependencies, environment, and database as the actual application.

### Typical Workflow

1. Edit code (mounted into container).
2. Run checks (optional):
   ```bash
   make qa
   ```
3. Commit changes  - pre-commit runs automatically.
4. Run tests:
   ```bash
   make test
   ```
5. For dependency changes:
   ```bash
   make poetry-add ARGS="package"
   make poetry-lock
   ```

### Git Branching & Commit Rules

Branching:
- `feature/<short-description>`
  Example: `feature/add-aggregation-endpoint`
- `fix/<short-description>`
  Example: `fix/transaction-rounding`
- `refactor/<short-description>`
  Example: `refactor/query-optimization`

For commit messages use: `<type>: <short description>`

Allowed types:
- `feat` - new functionality
- `fix` - bug fix
- `refactor` - internal improvements
- `test` - testing only
- `docs` - documentation updates
- `style` - formatting only
- `chore` - config/CI/dependency updates
