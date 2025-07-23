#!/bin/bash

poetry run python manage.py makemigrations
poetry run python manage.py migrate
bash populate_db_with_test_data.sh
bash entrypoint.sh
