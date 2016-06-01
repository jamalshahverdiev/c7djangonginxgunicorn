#!/usr/bin/env python2.7

import sys
import os
import jinja2
import time
import re

from fabric.api import *
from fabric.tasks import execute
import getpass

templateLoader = jinja2.FileSystemLoader( searchpath="/" )
templateEnv = jinja2.Environment( loader=templateLoader )
TEMPSTFILE = os.getcwd()+'/jinja2temps/settings.py'
TEMPGFILE = os.getcwd()+'/jinja2temps/gunicorn.service'
TEMPDVHFILE = os.getcwd()+'/jinja2temps/ngdjvhost.conf'

tempst = templateEnv.get_template( TEMPSTFILE )
tempgu = templateEnv.get_template( TEMPGFILE )
tempdh = templateEnv.get_template( TEMPDVHFILE )

env.host_string = raw_input('Please enter WEB server IP address: ')
env.user = raw_input('Please enter username for UNIX/Linux server: ')
env.password = getpass.getpass()
sitename = raw_input('Please enter site name: ')

password = ""
correctPassword = "1"
def passwordchecker(passwd=password, corpass=correctPassword):
    while passwd != corpass:
        print('Entered passwords must be the same. Please enter passwords again. ')
        passwd = getpass.getpass('Please enter password: ')
        corpass = getpass.getpass('Please repeat password: ')
        if passwd == corpass:
            print('The password set successfully!')
            break
        print('Entered passwords must be the same. Please enter passwords again. ')
#def passwordchecker(passwd=password, corpass=correctPassword):
#    while passwd != corpass:
#        print('Entered passwords must be the same. Please enter passwords again. ')
#        passwd = getpass.getpass('Please enter password: ')
#        corpass = getpass.getpass('Please repeat password: ')
#        if re.search(r'[a-z]', passwd) and re.search(r'[A-Z]', passwd) and re.search(r'\d', passwd):
#            print('The password policy is worked!!!')
#            pass
#        else:
#            print(' Minimal length of password is 8. One upper case, one number and one lower case must be there... ')
#            continue
#        if passwd == corpass:
#            print('The password set successfully!')
#            break
#        print('Entered passwords must be the same. Please enter passwords again. ')

with settings(
        hide('warnings', 'running', 'stdout', 'stderr'), 
        warn_only=True
):
    osver = run('uname -s')
    lintype = run('cat /etc/redhat-release | awk \'{ print $1 }\'')
    if osver == 'Linux' and lintype == 'CentOS':
        print(' This is CentOS server...')
        print(' Please be patient it will take some time!!!')
        getlngdpack = run('which nginx')
        ngpidfile = run('cat /var/run/nginx.pid')
        ngpid = run('ps waux | grep nginx | grep root | grep -v grep | awk \'{ print $2 }\'')
        if getlngdpack == '/usr/sbin/nginx' and ngpidfile == ngpid:
            print(' You have already installed and running Nginx web server...')
            print(' If you want add new VirtualHost, please use ./add-vhost-djgun.py script.')
            sys.exit()
        elif getlngdpack != '/usr/sbin/nginx':
            run('yum -y install epel-release')
            run('mkdir /var/www')
            run('yum -y install python-pip python-devel postgresql-server postgresql-devel postgresql-contrib gcc nginx')
            run('postgresql-setup initdb')
            put(os.getcwd()+'/jinja2temps/pg_hba.conf', '/var/lib/pgsql/data/pg_hba.conf')
            run('systemctl start postgresql ; systemctl enable postgresql')
            ip = run('ifconfig `ifconfig | head -n1 | cut -f1 -d\':\'` | grep \'inet \' | awk \'{ print $2 }\'')
            name = run('hostname')
            run('echo \"'+ip+' '+name+'.lan '+name+'\" >> /etc/hosts')
            psqlpidf = run('ps waux|grep pgsql | grep -v grep | grep -v safe | awk \'{ print $2 }\'')
            psqlpid = run('cat /var/run/postgresql/.s.PGSQL.5432.lock | head -1')
            if psqlpidf == psqlpid:
                print('PostgreSQL service already running...')
                pass
            else:
                print('PostgreSQL service is not running...')
                sys.exit()
            sitedb = raw_input('Enter name for new database: ')
            sitedbuser = raw_input('Enter new user name for access '+sitedb+': ')
            sitedbpasswd = getpass.getpass('Enter pass for '+sitedbuser+': ')
            sitedbpasswd1 = getpass.getpass('Repeat pass for '+sitedbuser+': ')
            passwordchecker(sitedbpasswd, sitedbpasswd1)
            oversitepass = "'\\'%s\\''" % sitedbpasswd
            run('su - postgres bash -c "psql -c \'CREATE DATABASE '+sitedb+';\'"')
            run('su - postgres bash -c "psql -c \'CREATE USER '+sitedbuser+' WITH PASSWORD '+oversitepass+';\'"')
            run('su - postgres bash -c "psql -c \'GRANT ALL PRIVILEGES ON DATABASE '+sitedb+' TO '+sitedbuser+';\'"')
            # psql -U linuser -h 127.0.0.1 lindb    
            run('pip install --upgrade pip')
            run('pip install virtualenv')
            run('mkdir /var/www/'+sitename+'')
            nsite = sitename.split('.')[0]
            run('cd /var/www/'+sitename+'; virtualenv '+sitename+'env; source '+sitename+'env/bin/activate; pip install django gunicorn psycopg2; django-admin.py startproject '+nsite+' .')
            skey = run('cat /var/www/'+sitename+'/'+nsite+'/settings.py | grep SECRET_KEY | awk \'{ print $3 }\'')
            tempstVars = { "sname" : sitename, "projname" : nsite, "secretkey" : skey, "database" : sitedb, "dbuser" : sitedbuser, "dbpass" : sitedbpasswd, }
            outputstText = tempst.render( tempstVars )
            with open(os.getcwd()+"/output/settings.py", "wb") as settingsfile:
                settingsfile.write(outputstText)
            put(os.getcwd()+'/output/settings.py', '/var/www/'+sitename+'/'+nsite+'/settings.py')
            djadm = raw_input('Please enter admin username for DjangoAdmin: ')
            djem = raw_input('Please enter admin email for DjangoAdmin: ')
            print('Minimal length of password is 8. One upper case, one number and one lower case must be there... ')
            djadmpass = getpass.getpass('Please enter Django admin password for '+djadm+' user: ') 
            djadmpassrep = getpass.getpass('Please repeat Django admin password for '+djadm+' user: ')
            passwordchecker(djadmpass, djadmpassrep)
            run('cd /var/www/'+sitename+'; source '+sitename+'env/bin/activate; ./manage.py makemigrations ; ./manage.py migrate ; echo "from django.contrib.auth.models import User; User.objects.create_superuser(\''+djadm+'\', \''+djem+'\', \''+djadmpass+'\')" | ./manage.py shell')
            run('cd /var/www/'+sitename+'; source '+sitename+'env/bin/activate; echo -e "yes" | ./manage.py collectstatic')
            outputguText = tempgu.render( tempstVars )
            with open(os.getcwd()+"/output/gunicorn.service", "wb") as gunfile:
                gunfile.write(outputguText)
            put(os.getcwd()+'/output/gunicorn.service', '/etc/systemd/system/'+nsite+'gunicorn.service')
            run('systemctl start '+nsite+'gunicorn ; systemctl enable '+nsite+'gunicorn')
            gunpid = run('systemctl status '+nsite+'gunicorn | grep running | awk \'{ print $2 }\'')
            if gunpid == 'active':
                print('Congratulations, your Gunicorn service is already working!!!')
            else:
                print('There is some errors. Please check logs by "journalctl -xe" command.')
            run('mkdir /etc/nginx/sites-enabled/ /etc/nginx/sites-available/')
            outputdvhText = tempdh.render( tempstVars )
            with open(os.getcwd()+"/output/djngvhost.conf", "wb") as djvfile:
                djvfile.write(outputdvhText)
            put(os.getcwd()+'/output/djngvhost.conf', '/etc/nginx/sites-available/'+sitename+'.conf')
            run('ln -s /etc/nginx/sites-available/* /etc/nginx/sites-enabled/')
            put(os.getcwd()+'/jinja2temps/djnginx.conf', '/etc/nginx/nginx.conf')
            run('usermod -a -G root nginx ; chmod 710 /var/www/ ; systemctl start nginx ; systemctl enable nginx')
            ngstat = run('systemctl status nginx | grep running | awk \'{ print $2 }\'') 
            if ngstat == 'active':
                print('Congratulations, you have already installed and configured nGinx with Gunicorn!!!')
            else:
                print('There is some errors. Please check nGinx "error_log" file.')
