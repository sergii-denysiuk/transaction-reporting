FROM python:3.13-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# Environment for Poetry
ENV POETRY_VERSION=2.2.1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install Poetry
RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app

# Copy poetry files first to leverage Docker layer caching
COPY pyproject.toml poetry.lock* /app/

# Install dependencies (into the global env inside the container)
RUN poetry install --no-interaction --no-ansi

# Copy the rest of the project
COPY . /app

# Expose Django port
EXPOSE 8000

# Start app
CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:8000"]
