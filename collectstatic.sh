#!/usr/bin/env sh

# All this environment variables need to be defined to run collectstatic
export ALLOWED_HOSTS=nothing
export CORS_ORIGIN_WHITELIST=nothing
export DATABASE_ENGINE=postgresql
export DATABASE_NAME=nothing
export DATABASE_USER=nothing
export DATABASE_PASSWORD=nothing
export DATABASE_HOST=nothing
export DATABASE_PORT=nothing
export DJANGO_SETTINGS_MODULE=bifrost-api.settings.production

python manage.py collectstatic --no-input
