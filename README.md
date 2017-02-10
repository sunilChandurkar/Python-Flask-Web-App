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

CHANHGING SSH

sudo nano /etc/ssh/sshd_config

Change port from 22 to 2200 and add Allowusers grader at the end of the file.

Disable root user by commenting out this line.

#PermitRootLogin without-password

sudo service ssh restart


Software Installed
apache2
libapache2-mod-wsgi
git
python-pip
Flask
oauth2client
postgresql 
python-psycopg2
python-sqlalchemy
