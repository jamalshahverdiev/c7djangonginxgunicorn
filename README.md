Python Django with nginx and gunicron.
I wope you already installed fresh Centos7 and disabled firewalld, SeLinux and Already updated your system.

Script requires server's ip address, username, password and FQDN at initial run. Script is intended for Centos7 OS.Script checks and installs PostgreSQL, Python and Nginx web server if not installed.After starting PostgreSQL, input is prompted for db name and credentials.Script install all required python libraries automatically for Django.Then script prompts for  django admin user/password to assign. Script starts all services and exits.
