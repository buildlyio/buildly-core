#!/usr/bin/env bash

set -e

bash scripts/tcp-port-wait.sh $DATABASE_HOST $DATABASE_PORT

echo $(date -u) "- Migrating"
python manage.py makemigrations
python manage.py migrate

echo $(date -u) "- Load Initial Data"
python manage.py loadinitialdata

echo $(date -u) "- Collect Static"
python manage.py collectstatic --no-input

echo $(date -u) "- Running the server"
gunicorn -b 0.0.0.0:8080 buildly.wsgi
