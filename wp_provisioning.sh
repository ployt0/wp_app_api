apt-get update
# Sure, we _could_ try and add a user, but they'd be sudoing anyway, kind of
# defeating the purpose. default-mysql-client for manual db queries from here.
apt-get install -y openssh-server sudo default-mysql-client
service --status-all
sed -i "s/^#* *PermitRootLogin.*$/PermitRootLogin yes/" /etc/ssh/sshd_config
cat /etc/ssh/sshd_config | grep PermitRootLogin
echo "root:password" | chpasswd
/etc/init.d/ssh start || /etc/init.d/ssh restart


openssl req -new -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -days 365 -nodes -x509 \
    -subj "/CN=localhost" \
    -keyout /etc/ssl/private/apache-selfsigned.key -out /etc/ssl/certs/apache-selfsigned.crt

chown www-data:www-data /var/www/html/wp-config.php
chown root:root /etc/apache2/conf-available/ssl-params.conf
chown root:root /etc/apache2/sites-available/wordpress.conf


a2enmod ssl
a2enmod headers
a2enmod rewrite
a2ensite wordpress
a2enconf ssl-params
a2dissite 000-default

#systemctl reload apache2
# Can't restart apache in the docker because it is the fg process.
# Instead, restart the whole docker, which the Sys5 init does:
#/etc/init.d/apache2 restart


