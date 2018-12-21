#!/usr/bin/env bash

echo $(date -u) "- Migrating"
python manage.py migrate

echo $(date -u) "- Load Initial Data"
python manage.py loadinitialdata

echo $(date -u) "- Collect Static"
python manage.py collectstatic --no-input

# Remove it later. ONLY FOR DEMO!
echo $(date -u) "- Creating admin user"
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(email='admin@example.com').delete(); User.objects.create_superuser('admin', 'admin@example.com', 'ttmtola1977')"

echo "Starting celery worker"
celery_cmd="celery -A gateway worker -l info -f celery.log"
$celery_cmd &

echo $(date -u) "- Running the server"
gunicorn -b 0.0.0.0:8080 bifrost-api.wsgi
