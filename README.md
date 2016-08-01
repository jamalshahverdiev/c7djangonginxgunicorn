<html>
<meta charset="utf-8">
Python Django with nginx and gunicron.
I hope you already installed fresh Centos7 and disabled firewalld, SeLinux and Already updated your system.

Script requires server's <b>IP</b> address, <b>username</b>, <b>password</b> and <b>FQDN</b> at initial run. Script is intended for Centos7 operation system. If PostgreSQL, Python and Nginx web server is not installed to the server, script will check this and start to install. You must write input database credentials for new virtual host. Python libraries for Django will be installed automatically. Then we must write django <b>admin user/password</b>. At the end script will start all services and exit.
</html>
