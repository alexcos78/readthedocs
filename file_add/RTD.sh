#!/bin/bash
cd /root/readthedocs.org
export HOME=/root
PROFILE=$HOME/readthedocs.org/venv/bin/activate
source $PROFILE
python manage.py runserver 0.0.0.0:80
