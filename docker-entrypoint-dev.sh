#!/bin/bash

echo "Migrate"
python manage.py migrate

if [ "$nginx" == "true" ]; then
    echo "Collect static"
    python manage.py collectstatic --no-input
fi

echo "Creating admin user"
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(email='admin@humanitec.com').delete(); User.objects.create_superuser('admin', 'admin@humanitec.com', 'admin')"

echo "Loading basic initial data"
python manage.py loadinitialdata

echo "Running the server"
if [ "$nginx" == "true" ]; then
    PYTHONUNBUFFERED=1 gunicorn -b 0.0.0.0:8080 bifrost-api.wsgi --reload
else
    PYTHONUNBUFFERED=1 python manage.py runserver 0.0.0.0:8080
fi
