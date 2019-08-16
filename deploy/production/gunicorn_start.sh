#!/bin/bash

NAME="portfolio"
VENV_NAME="django"                                    # Name of the application
DJANGODIR=/www/$NAME/$NAME                            # Django project directory
VENVDIR=/www/$NAME/$VENV_NAME                         # Django project directory
SOCKFILE=/www/$NAME/run/gunicorn.sock                 # we will communicte using this unix socket
USER=deploy                                           # the user to run as
GROUP=deploy                                          # the group to run as
NUM_WORKERS=3                                         # how many worker processes should Gunicorn spawn
DJANGO_SETTINGS_MODULE="$NAME.settings.production"    # which settings file should Django use
DJANGO_WSGI_MODULE="$NAME.wsgi"                       # WSGI module name
echo "Starting $NAME as `whoami`"


# Activate the virtual environment

cd $DJANGODIR
source $VENVDIR/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH


# Create the run directory if it doesn't exist

RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR


# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)

gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER \
  --bind=unix:$SOCKFILE \
  --log-level=debug \
  --log-file=- \
  --reload
