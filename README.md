# Transaction Reporting Backend

APIs for retrieving and aggregating transaction data.


## Requirements

For local development, Docker and Docker Compose are used.

Project dependencies:
- Python 3.13
- PostgreSQL 18
- Poetry 2.2

## Project Structure

```bash
transaction-reporting/
├── envs/
│   ├── .env.example        # Template environment file
│   └── .env                # Actual environment variables (ignored by git)
├── transaction_reporting/  # Django project configuration
├── transactions/           # Transactions app
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── pyproject.toml
└── README.md
```


## Environment Variables

Environment variables are stored in: `envs/.env`
Create this file manually or copy from the template: `cp envs/.env.example envs/.env`


## First-Time Setup

These steps are required only when setting up the project for the first time.

1.	Create the environment file: `cp envs/.env.example envs/.env`
2.	Build the application: `make build`
3.	Start the application: `make up`
4.	Run database migrations: `make migrate`

The server is now available at: http://localhost:8000/￼


## Development Commands

All daily development actions use Docker Compose and the Makefile shortcuts.

- Rebuild Docker images: `make build`
- Start the app: `make up` (or detached `make up-detached`)
- Stop all containers: `make down`
- Follow logs: `make logs`
- Run migrations: `make migrate`
- Create new migrations: `make makemigrations`
- Run tests: `make test`
- Open a bash shell inside the app container: `make bash`
- Open Django shell: `make shell`


## Git Branching & Commit Rules

### Branching Strategy

- Feature branches: `feature/<short-description>`
  Example: `feature/add-transaction-endpoint`
- Bugfix branches: `fix/<short-description>`
- Refactor branches: `refactor/<short-description>`

### Commit Message Format

Use clean, descriptive commit messages.

Format: `<type>: <short description>`

Allowed types:
- `feat` - new functionality
  Example: `feat: add transaction list endpoint`
- `fix` - bug fix
  Example: `fix: correct amount parsing logic`
- `refactor` - code change without altering behavior
  Example: `refactor: split transaction serializers into separate module`
- `test` - add or update tests
  Example: `test: add aggregation endpoint test`
- `docs` - documentation changes
  Example: `docs: update README with Docker instructions`
- `style` - formatting (black, isort), no code changes
  Example: `style: run black and isort on project`
- `chore` - config updates, dependency bumps, CI adjustments
