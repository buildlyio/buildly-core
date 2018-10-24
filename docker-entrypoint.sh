#!/bin/bash

echo $(date -u) "- Migrating"
python manage.py migrate

echo $(date -u) "- Collect Static"
python manage.py collectstatic --no-input

echo $(date -u) "- Running the server"
gunicorn -b 0.0.0.0:8080 bifrost-api.wsgi

