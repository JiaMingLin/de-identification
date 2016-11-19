#!/bin/bash

service mysql restart
redis-server --daemonize yes
service supervisor restart

mkdir /opt/de-identification/log/
touch /opt/de-identification/log/worker.log

python manage.py runserver 0.0.0.0:8080