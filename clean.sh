#!/bin/bash

# clear mysql
mysql -e "drop database de_identification;"
mysql -e "create database de_identification;"

# remove files
rm -rf mediate_data/*

# remove migrate data
rm  api/migrations/00*

python manage.py makemigrations
python manage.py migrate
