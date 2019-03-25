#!/bin/bash

# reset migration (all data in these tables will be removed)
python manage.py migrate admin zero
python manage.py migrate authtoken zero
python manage.py migrate guardian zero
python manage.py migrate social_django zero
python manage.py migrate oauth2_provider 0003
python manage.py migrate --fake oauth2_provider 0001 # because of IntegrityError: column "user_id" contains null values
python manage.py migrate oauth2_provider zero

# redo migrations
python manage.py migrate