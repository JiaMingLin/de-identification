#!/bin/bash

service mysql restart
# clear mysql
mysql -e "drop database de_identification;"
mysql -e "create database de_identification;"

# remove files
rm -rf mediate_data/*

# remove migrate data
rm  api/migrations/00*

# remove logs
rm log/*

python manage.py makemigrations
python manage.py migrate
