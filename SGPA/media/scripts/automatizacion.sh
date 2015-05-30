#!/bin/bash
# -*- ENCODING: UTF-8 -*-
echo "Bienvenido a SGPA"
#Instalar Python
sudo apt-get install python2.7

#Instalar Pycharm
#wget -q -O - http://archive.getdeb.net/getdeb-archive.key | sudo apt-key add -
#sudo sh -c 'echo "deb http://archive.getdeb.net/ubuntu trusty-getdeb apps" >> /etc/apt/sources.list.d/getdeb.list'
#sudo apt-get update
#sudo apt-get install pycharm

#Instalar pgadmin3
sudo apt-get install postgresql pgadmin3
sudo apt-get install python-psycopg2
#Instalar Django
sudo apt-get install python-pip
sudo pip install Django==1.7.7

#Instalar Librerias para el burndownChart
sudo apt-get install python-numpy
sudo apt-get install python-matplotlib

#Crear Usuario de Base de Datos
#sudo su postgres
#createuser udesarrollo
#psql -l
#psql template1
#alter role udesarrollo with password '12345';
#alter role udesarrollo with superuser;

#Instalar git
sudo apt-get install git
sudo apt-get install xclip

#Instalacion del entorno virtual
sudo aptitude install libapache2-mod-wsgi
sudo service apache2 restart
sudo apt-get install python-virtualenv

export WORKON_HOME=$HOME/entornoVirtual/
mkdir -p $WORKON_HOME
sudo virtualenv --no-site-packages $WORKON_HOME/venv
source $WORKON_HOME/venv/bin/activate

git init
git clone https://github.com/Lili90/repois2.git

echo 'copiamos el entorno al proyecto'
#copiamos el entorno a el proyecto
cp -R $HOME/entornoVirtual/venv/ $HOME/repois2/
cp $HOME/repois2/SGPA/media/scripts/mySite.conf $HOME/

cd $HOME/repois2/
#ir a la carpeta del proyecto e iniciar el entorno virtual
######################################
###Hacemos el menu para los tag#######
######################################

clear
osch=0
echo "1. iteracion 1"
read osch

if [ $osch -eq 1 ] ; then
    echo "iteracion 1"
    sleep 1s
    git checkout 2b6a4a6c166d9a1881f035ac4fb41bfe32e2abe8
    clear
    echo 'creando el usuario udesarrollo, ingrese password: 12345'
    sleep 1s
    sudo -u postgres dropdb SGPA_db
    sudo -u postgres dropuser udesarrollo
    sudo -u postgres createuser --superuser udesarrollo -P
    clear
    echo 'creando la base de datos'
    sudo -u postgres createdb SGPA_db --owner=uderarrollo

elif [ $osch -eq 5 ]
then
    echo "iteracion 5"
    sleep 1s
    git checkout 663ff4074190b4cea18d262285e144c1751c61dc
    clear
    echo 'creando el usuario, ingrese password: 12345'
    sleep 1s
    #crear un usuario en la base de datos
    #eliminamos si existe una base de datos llamada produccion
    sudo -u postgres dropdb SGPA_db_produccion
    sudo -u postgres dropuser udesarrollo
    sudo -u postgres createuser --superuser udesarrollo -P
    sudo -u postgres createdb SGPA_db_produccion --owner=udesarrollo
    #cargar la base de datos
    #pg_restore -i -h localhost -p 5432 -U udesarrollo -d SGPA_db_produccion -v "poblado_tablas_produccion.backup"
fi

#sincronizar la base de datos
python manage.py syncdb

echo 'movemos el servidor a lugar que debe estar'
sudo rm -rf /var/www/repois2/
cd $HOME
sudo mv -f -v $HOME/repois2/ /var/www/repois2/

####################################################
###### Configuracion de apache #####################
####################################################
echo 'configurando apache'
#agregamos la direccion al archivo hosts
echo 'ingrese la linea 127.0.0.1	sgpa.com'
sleep 1s
sudo nano /etc/hosts

echo 'reiniciamos apache'
sudo mv -v $HOME/mySite.conf /etc/apache2/sites-available/
sudo a2dissite mySite.conf
sudo service apache2 restart
sudo a2ensite mySite.conf
sudo service apache2 restart


echo 'abriendo el navegador'
sudo apt-get install libgnome2-bin
gnome-open http://sgpa.com

