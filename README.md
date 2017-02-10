SERVER AT AWS

Server at IP Address of the App 52.32.162.160

ec2-52-32-162-160.us-west-2.compute.amazonaws.com

UPDATE ALL PACKAGES

sudo apt-get update 

sudo apt-get upgrade

ADD A USER

sudo adduser grader

sudo cp ~/.ssh/authorized_keys /home/grader/.ssh/authorized_keys

provide proper permissions

sudo chown grader /home/grader/.ssh

sudo chgrp grader /home/grader/.ssh

sudo chown grader /home/grader/.ssh/authorized_keys

sudo chgrp grader /home/grader/.ssh/authorized_keys

sudo chmod 700 /home/grader/.ssh

sudo chmod 644 /home/grader/.ssh/authorized_keys

ENABLE SUDO FOR GRADER

sudo nano /etc/sudoers.d/grader

grader ALL=(ALL) PASSWD: ALL


CONFIGURE UFW

sudo ufw default deny incoming

sudo ufw default allow outgoing

sudo ufw allow 2200

sudo ufw allow 80

sudo ufw allow 123

sudo ufw enable


INSTALL SOFTWARE

sudo apt-get install apache2

sudo apt-get install libapache2-mod-wsgi

sudo apt-get install git

sudo apt-get install python-pip

sudo pip install Flask

sudo pip install oauth2client

sudo apt-get install postgresql 

sudo apt-get install python-psycopg2

sudo apt-get install python-sqlalchemy

VIRTUAL HOST

sudo nano /etc/apache2/sites-available/itemcatalog.conf

<VirtualHost *:80>
                ServerName 52.32.162.160
                ServerAlias ec2-52-32-162-160.us-west-2.compute.amazonaws.com
                ServerAdmin grader@52.32.162.160
                WSGIScriptAlias / /var/www/itemcatalog/itemcatalog.wsgi
                <Directory /var/www/itemcatalog/itemcatalog/>
                        Order allow,deny
                        Allow from all
                </Directory>
                Alias /static /var/www/itemcatalog/itemcatalog/static
                <Directory /var/www/itemcatalog/itemcatalog/static/>
                        Order allow,deny
                        Allow from all
                </Directory>
                ErrorLog ${APACHE_LOG_DIR}/error.log
                LogLevel warn
                CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>

WSGI FILE

cd /var/www/itemcatalog

sudo nano itemcatalog.wsgi


#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/itemcatalog/itemcatalog/")

from project import app as application
application.secret_key = 'mysecret'


CHANHGING SSH

sudo nano /etc/ssh/sshd_config

Change port from 22 to 2200 and add Allowusers grader at the end of the file.

Disable root user by commenting out this line.

#PermitRootLogin without-password

sudo service ssh restart

sudo service apache2 restart 


