#!/bin/bash

NAME="portfolio"                                        # Name of the project
VENV_NAME="django"                                      # Name of the application
DJANGODIR=/www/$NAME/$NAME                              # Django project directory
VENVDIR=/www/$NAME/$VENV_NAME                           # Django project directory
SOCKFILE=/www/$NAME/run/gunicorn.sock                   # we will communicte using this unix socket
USER=deploy                                             # the user to run as
GROUP=deploy                                            # the group to run as
NUM_WORKERS=3                                           # how many worker processes should Gunicorn spawn
DJANGO_SETTINGS_MODULE="portfolio.settings.production"  # which settings file should Django use
DJANGO_WSGI_MODULE="portfolio.wsgi"                     # WSGI module name
echo "Starting $NAME as `whoami`"


cd $DJANGODIR
source $VENVDIR/bin/activate
export CELERYD_CHDIR=$DJANGODIR
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE && /www/$NAME/$VENV_NAME/bin/celery --app=$NAME.celery:app worker --loglevel=INFO
