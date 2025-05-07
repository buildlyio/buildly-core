#!/usr/bin/env bash

# All this environment variables need to be defined to run collectstatic
export ALLOWED_HOSTS=nothing
export CORS_ORIGIN_WHITELIST=nothing
export HUBSPOT_API_KEY=nothing
export DATABASE_ENGINE=postgresql
export DATABASE_NAME=nothing
export DATABASE_USER=nothing
export DATABASE_PASSWORD=nothing
export DATABASE_HOST=nothing
export DATABASE_PORT=nothing
export DJANGO_SETTINGS_MODULE=buildly.settings.production
export SECRET_KEY=nothing
export TOKEN_SECRET_KEY=nothing
export HUBSPOT_API_KEY=nothing

python manage.py collectstatic --no-input
