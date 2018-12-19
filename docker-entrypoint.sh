#!/bin/bash

echo $(date -u) "- Migrating"
python manage.py migrate

echo $(date -u) "- Load Initial Data"
python manage.py loadinitialdata

echo $(date -u) "- Collect Static"
python manage.py collectstatic --no-input

echo "Starting celery worker"
celery_cmd="celery -A gateway worker -l info -f celery.log"
$celery_cmd &

echo $(date -u) "- Running the server"
gunicorn -b 0.0.0.0:8080 bifrost-api.wsgi
