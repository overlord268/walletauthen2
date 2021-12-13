#!/bin/bash

NAME="wallethauthen2" # Nombre dela aplicación
DJANGODIR=/root/wallethauthen2 # Ruta dela carpeta donde esta la aplicación reemplazar <user> con el nombre de usuario
SOCKFILE=/root/run/gunicorn.sock # Ruta donde se creará el archivo de socket unix para comunicarnos
USER=root # Usuario con el que vamos a correr laapp
GROUP=root # Grupo con el quese va a correr laapp
NUM_WORKERS=3 # Número de workers quese van a utilizar para correr la aplicación
DJANGO_SETTINGS_MODULE=walletauth.settings # ruta de los settings
DJANGO_WSGI_MODULE=walletauth.wsgi # Nombre del módulo wsgi

echo "Starting $NAME as `whoami`"

# Activar el entorno virtual
cd $DJANGODIR
source wallethauthen2ENV/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Crear la carpeta run si no existe para guardar el socket linux
RUNDIR=$(dirname $SOCKFILE)
test -d$RUNDIR || mkdir -p $RUNDIR

# Iniciar la aplicación django por medio de gunicorn
exec ../bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --bind=unix:$SOCKFILE \
  --log-level=debug \
  --log-file=-
