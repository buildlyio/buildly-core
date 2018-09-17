#!/bin/bash

echo $(date -u) " - Migrating"
python manage.py migrate

RESULT=$?
if [ $RESULT -ne 0 ]; then
    echo $(date -u) " - There was a problem migrating. Setting up the maintenance page"
    pushd templates/maintenance/; python -m SimpleHTTPServer 8000; popd
else
    echo $(date -u) " - Running the server in branch '$branch'"
    service nginx restart
    if [ "$branch" == "dev" ]; then
        gunicorn -b 0.0.0.0:8080 bifrost-api.wsgi --reload
    else
        gunicorn -b 0.0.0.0:8080 bifrost-api.wsgi
    fi
fi
