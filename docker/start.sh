#!/bin/bash

service mysql restart
python manage.py runserver 0.0.0.0:8080