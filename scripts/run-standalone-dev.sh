#!/usr/bin/env bash
# This script must not be used for production. Migrating, collecting static
# data, check database connection should be done by different jobs in
# at a different layer.

set -e

bash scripts/tcp-port-wait.sh $DATABASE_HOST $DATABASE_PORT

echo $(date -u) "- Migrating"
python manage.py makemigrations
python manage.py migrate

echo $(date -u) "- Load Initial Data"
python manage.py loadinitialdata

echo $(date -u) "- Running the server"
gunicorn -b 0.0.0.0:8080 --reload buildly.wsgi -w 2 --timeout 120
