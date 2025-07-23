#!/bin/bash

poetry run python manage.py makemigrations
poetry run python manage.py migrate
bash entrypoint.sh
