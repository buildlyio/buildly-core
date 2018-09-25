#!/bin/bash

echo $(date -u) "- Environment: $environment"
bash tcp-port-wait.sh $DATABASE_HOST $DATABASE_PORT

if [ "$environment" == "localhost" ]; then
    echo $(date -u) "- Migrating"
    python manage.py migrate

    RESULT=$?
    if [ $RESULT -ne 0 ]; then
        echo $(date -u) "- There was a problem migrating. Exiting."
        exit 1
    else
        echo $(date -u) "- Creating admin user"
        python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(email='admin@example.com').delete(); User.objects.create_superuser('admin', 'admin@example.com', 'admin')"

        echo $(date -u) "- Running the development server"
        PYTHONUNBUFFERED=1 python manage.py runserver 0.0.0.0:8080
    fi
else
    echo $(date -u) "- Running the server"
    gunicorn -b 0.0.0.0:8080 rules_service.wsgi
fi
