#!/usr/bin/env bash
#cd SGPA
#export DJANGO_SETTINGS_MODULE=settings.py
export PYTHONPATH=/usr/lib/python2.7:/usr/lib/python2.7/plat-x86_64-linux-gnu:/usr/lib/python2.7/lib-tk:/usr/lib/python2.7/lib-old:/usr/lib/python2.7/lib-dynload:/usr/local/lib/python2.7/dist-packages:/usr/lib/python2.7/dist-packages:/usr/lib/python2.7/dist-packages/PILcompat:/usr/lib/python2.7/dist-packages/gtk-2.0:/usr/lib/python2.7/dist-packages/ubuntu-sso-client:/home/gerardo/PycharmProjects/repois2/SGPA
cd apps/home
python -m unittest tests.py
