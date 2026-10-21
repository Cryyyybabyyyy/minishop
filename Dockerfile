# MiniShop – intentionally vulnerable lab image
# Runs as non-root, drops capabilities, no privileged mode.

FROM python:3.12-slim-bookworm

# Security: create non-root user
RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash appuser

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application source
COPY app/ ./app/
COPY tests/ ./tests/

# Ensure directories exist and are owned by appuser
RUN mkdir -p /app/instance /app/app/static/uploads \
    && chown -R appuser:appuser /app

# Drop to non-root
USER appuser

ENV FLASK_APP=app.wsgi:app
ENV PYTHONUNBUFFERED=1
ENV DATABASE_PATH=/app/instance/minishop.db
ENV UPLOAD_FOLDER=/app/app/static/uploads

EXPOSE 5000

# Gunicorn binds only to the container interface; host binding is controlled by Compose
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "2", "--timeout", "30", "app.wsgi:app"]
