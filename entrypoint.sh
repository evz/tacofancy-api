#!/bin/bash

set -e

flask --app tacofancy init-db
flask --app tacofancy preheat

gunicorn -b unix:/code/tacofancy.sock --log-level=debug 'tacofancy:create_app()'
