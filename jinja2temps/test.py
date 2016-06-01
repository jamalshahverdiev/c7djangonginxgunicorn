#!/usr/bin/env python

import sys
import os
import jinja2

from fabric.api import *
from fabric.tasks import execute
import getpass

#sitename = raw_input('Please enter site name: ')

#nsite = sitename.split('.')[0]
#print(nsite)

env.host_string = raw_input('Please enter WEB server IP address: ')
env.user = raw_input('Please enter username for UNIX/Linux server: ')
env.password = getpass.getpass()
#sitename = raw_input('Please enter site name: ')

with settings(
        hide('warnings', 'running', 'stdout', 'stderr'),
        warn_only=True
):
    sitedb = raw_input('Enter name for new database: ')
    sitedbuser = raw_input('Enter new user name for access '+sitedb+': ')
    sitedbpasswd = getpass.getpass('Enter pass for '+sitedbuser+': ')
    oversitepass = "'\\'%s\\''" % sitedbpasswd
    print(oversitepass)
    run('su - postgres bash -c "psql -c \'CREATE DATABASE '+sitedb+';\'"')
    run('su - postgres bash -c "psql -c \'CREATE USER '+sitedbuser+' WITH PASSWORD '+oversitepass+';\'"')
    run('su - postgres bash -c "psql -c \'GRANT ALL PRIVILEGES ON DATABASE '+sitedb+' TO '+sitedbuser+';\'"')
    djadm = raw_input('Please enter admin username for DjangoAdmin: ')
    djem = raw_input('Please enter admin email for DjangoAdmin: ')
    print('Minimal length of password is 8. One upper case and one lower case must be there... ')
    djadmpass = raw_input('Please enter admin password for '+djadm+' user: ')
    run('cd /var/www/linux.com; source linux.comenv/bin/activate; ./manage.py makemigrations ; ./manage.py migrate ; echo "from django.contrib.auth.models import User; User.objects.create_superuser(\''+djadm+'\', \''+djem+'\', \''+djadmpass+'\')" | ./manage.py shell')

