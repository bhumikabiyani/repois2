#!/bin/bash
# -*- ENCODING: UTF-8 -*-
echo "Bienvenido a SGPA"
#Instalar Python
sudo apt-get install python2.7

#Instalar Pycharm
wget -q -O - http://archive.getdeb.net/getdeb-archive.key | sudo apt-key add -
sudo sh -c 'echo "deb http://archive.getdeb.net/ubuntu trusty-getdeb apps" >> /etc/apt/sources.list.d/getdeb.list'
sudo apt-get update
sudo apt-get install pycharm

#Instalar pgadmin3
sudo apt-get install postgresql pgadmin3
sudo apt-get install python-psycopg2
#Instalar Django
sudo apt-get install python-pip
sudo pip install Django==1.7.7
#Instalar git
sudo apt-get install git

#Crear Usuario de Base de Datos
sudo su postgres
createuser udesarrollo
psql -l
psql template1
alter role udesarrollo with password '12345';
alter role udesarrollo with superuser;




