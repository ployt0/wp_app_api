load "vagrant_const_comms.rb"

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/focal64"
  config.vm.box_version = LOCKED_2004_BOX_VERSION
  config.vm.box_check_update = false
  config.vm.hostname = "testrunner"
  config.vm.network :forwarded_port, guest: 443, host: 8543
  config.vm.network :forwarded_port, guest: 22, host: 8212, id: 'ssh'

  config.vm.provision "file", source: "wp_provisioning.sh", destination: "/home/vagrant/wp_provisioning.sh"
  config.vm.provision "file", source: "wpdbsetup.sql", destination: "/home/vagrant/wpdbsetup.sql"
  config.vm.provision "file", source: "full_db_220727_0953.sql", destination: "/home/vagrant/current_db.sql"
  config.vm.provision "file", source: "wp-config.php", destination: "/home/vagrant/wp-config.php"
  config.vm.provision "file", source: "ssl-params.conf", destination: "/home/vagrant/ssl-params.conf"
  config.vm.provision "file", source: "wordpress.conf", destination: "/home/vagrant/wordpress.conf"

  config.vm.provision "Install pip, docker.", type: "shell", inline: <<-SHELL
apt-get update
apt-get install -y docker.io python3-pip
SHELL

  config.vm.provision "Create docker group and add.", type: "shell", privileged: false, inline: <<-SHELL
compgen -g | grep docker || sudo groupadd docker
sudo usermod -aG docker $USER
SHELL

  config.vm.provision "start mariadb", type: "shell", inline: <<-SHELL
docker run --name mariadb -e MYSQL_ROOT_PASSWORD=mypass -p 3306:3306 -d --restart unless-stopped mariadb:10.8.3-jammy
SHELL

# Despite adding vagrant to the docker group, we still need root or sudo.
  config.vm.provision "Provision WP container", type: "shell", inline: <<-SHELL
docker run -p 80:80 -p 443:443 -p 127.0.0.1:8066:22 --name mywp -d --restart unless-stopped wordpress:6.0.1
# Need to expose 443 and 80 to all to do the initial setup via Web UI.
mariadb_addy=$(docker inspect --format '{{ .NetworkSettings.IPAddress }}' mariadb)

sed -i "s/172.17.0.3/$mariadb_addy/" /home/vagrant/wp-config.php
docker cp /home/vagrant/wp-config.php mywp:/var/www/html/wp-config.php
docker cp /home/vagrant/ssl-params.conf mywp:/etc/apache2/conf-available/ssl-params.conf
docker cp /home/vagrant/wordpress.conf mywp:/etc/apache2/sites-available/wordpress.conf

docker exec -i mywp bash < /home/vagrant/wp_provisioning.sh
docker restart mywp
# SSHD won't restart itself without:
docker exec -i mywp /etc/init.d/ssh start

SHELL

  config.vm.provision "Sleep while mariadb especially, restarts.", type: "shell", inline: <<-SHELL
# 3s can be insufficient, 5s is ok. Busy waiting.
while ! docker exec mariadb mysql -uroot -pmypass -e "SELECT 1" >/dev/null 2>&1; do
    echo sleeping.
    docker ps
    sleep 1
done
SHELL

  config.vm.provision "Grab the TLS cert from WP", type: "shell", inline: <<-SHELL
  echo quit | openssl s_client -showcerts -servername "localhost" -connect localhost:443 > /vagrant/self-signed-cacert.crt
SHELL

  config.vm.provision "use WP's IP for DB user", type: "shell", inline: <<-SHELL
wp_addy=$(docker inspect --format '{{ .NetworkSettings.IPAddress }}' mywp)
echo "wp_addy = $wp_addy"
sed -i "s/wpdockerip/$wp_addy/" /home/vagrant/wpdbsetup.sql
cp /vagrant/tests/config_template.json /vagrant/tests/config.json
SHELL

  config.vm.provision "sql script", type: "shell", inline: <<-SHELL
docker exec -i mariadb mysql -uroot -pmypass < /home/vagrant/wpdbsetup.sql
docker exec -i mariadb mysql -uroot -pmypass wordpress < /home/vagrant/current_db.sql
SHELL

  config.vm.provision "shell", privileged: false, inline: <<-SHELL
echo "colo ron" > ~/.vimrc
SHELL

  config.vm.provision "Check coverage", type: "shell", privileged: false, inline: <<-SHELL
pip install -r /vagrant/requirements.txt
cd /vagrant/tests
export PYTHONPATH=/vagrant
/home/vagrant/.local/bin/coverage run --source="../wp_api" -m pytest
/home/vagrant/.local/bin/coverage report -m --fail-under=95
SHELL

end

