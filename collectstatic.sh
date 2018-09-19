#!/usr/bin/env sh

# All this environment variables need to be defined to run collectstatic
export ALLOWED_HOSTS=nothing
export CORS_ORIGIN_WHITELIST=nothing
export DATABASE_NAME=nothing
export DATABASE_PORT=nothing
export DATABASE_USER=nothing
export DEFAULT_FROM_EMAIL=nothing
export DEFAULT_REPLY_TO=nothing
export DATABASE_ENGINE=postgresql
export DJANGO_SETTINGS_MODULE=bifrost.settings.production

python manage.py collectstatic --no-input
