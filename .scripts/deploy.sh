#!/bin/bash
set -e

echo "Deployment started ..."

# Pull the latest version of the app
echo "Copying New changes...."
git pull origin master
echo "New changes copied to server !"

# Activate Virtual Env
#Syntax:- source virtual_env_name/bin/activate
source env/bin/activate
echo "Virtual env 'env' Activated !"

echo "Installing Dependencies..."
pip install -r requirements.txt --no-input

echo "Clearing Cache..."
python3 manage.py clean_pyc
python3 manage.py clear_cache

echo "Serving Static Files..."
python3 manage.py collectstatic --noinput --settings=DilemmaPlatform.settings.prod

echo "Running Database migration..."
python3 manage.py migrate --settings=DilemmaPlatform.settings.prod


# Deactivate Virtual Env
deactivate
echo "Virtual env 'mb' Deactivated !"

echo "Reloading App..."

#kill -HUP `ps -C gunicorn fch -o pid | head -n 1`
ps aux |grep gunicorn |grep dilemmapp | awk '{ print $2 }' |xargs kill -HUP

echo "Deployment Finished !"
