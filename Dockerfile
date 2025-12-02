FROM python:3.13-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# Environment for Poetry + Python behavior
ENV POETRY_VERSION=2.2.1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app:${PYTHONPATH}"

# Install Poetry
RUN pip install "poetry==$POETRY_VERSION"

# Create non-root user and app directory
RUN addgroup --system django && adduser --system --ingroup django django \
    && mkdir -p /app && chown -R django:django /app

WORKDIR /app

# Copy poetry files first to leverage Docker layer caching
COPY pyproject.toml poetry.lock* /app/

# Install dependencies into the global env inside the container
RUN poetry install --no-interaction --no-ansi

# Copy the rest of the project
COPY . /app
RUN chown -R django:django /app

# Switch to non-root user
USER django

# Expose Django port
EXPOSE 8000

# Start app (for dev / case-study)
CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:8000"]
