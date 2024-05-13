# sudo apt-get update
# sudo apt-get full-upgrade
# sudo apt-get install -y dhcpcd5 lighttpd hostapd dnsmasq iptables-persistent vnstat qrencode php7.0-cgi jq isoquery 

# sudo lighttpd-enable-mod fastcgi-php
# sudo service lighttpd force-reload
# sudo systemctl restart lighttpd.service

# sudo rm -rf /var/www/html
# sudo git clone https://github.com/RaspAP/raspap-webgui /var/www/html

# sudo sed -i 's/$logfile = escapeshellcmd($_POST['logfile']);/$logfile = $_POST['logfile']/' /var/www/html/ajax/logging/clearlog.php
# sudo sed -i 's/$ovpncfg_id = escapeshellcmd($_POST['cfg_id']);/$ovpncfg_id = $_POST['cfg_id'];/' /var/www/html/ajax/openvpn/activate_ovpncfg.php
# sudo sed -i 's/$ovpncfg_id = escapeshellcmd($_POST['cfg_id']);/$ovpncfg_id = $_POST['cfg_id'];/' /var/www/html/ajax/openvpn/del_ovpncfg.php

# WEBROOT="/var/www/html"
# CONFSRC="$WEBROOT/config/50-raspap-router.conf"
# LTROOT=$(grep "server.document-root" /etc/lighttpd/lighttpd.conf | awk -F '=' '{print $2}' | tr -d " \"")

# HTROOT=${WEBROOT/$LTROOT}
# HTROOT=$(echo "$HTROOT" | sed -e 's/\/$//')
# awk "{gsub(\"/REPLACE_ME\",\"$HTROOT\")}1" $CONFSRC > /tmp/50-raspap-router.conf
# sudo cp /tmp/50-raspap-router.conf /etc/lighttpd/conf-available/

# sudo ln -s /etc/lighttpd/conf-available/50-raspap-router.conf /etc/lighttpd/conf-enabled/50-raspap-router.conf
# sudo systemctl restart lighttpd.service

cd /var/www/html
# sudo cp installers/raspap.sudoers /etc/sudoers.d/090_raspap

# sudo mkdir /etc/raspap/
# sudo mkdir /etc/raspap/backups
# sudo mkdir /etc/raspap/networking
# sudo mkdir /etc/raspap/hostapd
# sudo mkdir /etc/raspap/lighttpd
# sudo mkdir /etc/raspap/system

# sudo chown -R www-data:www-data /var/www/html
# sudo chown -R www-data:www-data /etc/raspap

# sudo mv installers/enablelog.sh /etc/raspap/hostapd
# sudo mv installers/disablelog.sh /etc/raspap/hostapd
# sudo mv installers/servicestart.sh /etc/raspap/hostapd
# sudo mv installers/debuglog.sh /etc/raspap/system

sudo chown -c root:root /etc/raspap/hostapd/*.sh
sudo chmod 750 /etc/raspap/hostapd/*.sh

# sudo chown -c root:root /etc/raspap/system/*.sh
# sudo chmod 750 /etc/raspap/system/*.sh

# sudo cp installers/configport.sh /etc/raspap/lighttpd
# sudo chown -c root:root /etc/raspap/lighttpd/*.sh

# sudo mv installers/raspapd.service /lib/systemd/system
# sudo systemctl daemon-reload
# sudo systemctl enable raspapd.service

# sudo mv /etc/default/hostapd ~/default_hostapd.old
# sudo cp /etc/hostapd/hostapd.conf ~/hostapd.conf.old
# sudo cp config/hostapd.conf /etc/hostapd/hostapd.conf
# sudo cp config/090_raspap.conf /etc/dnsmasq.d/090_raspap.conf
# sudo cp config/090_wlan0.conf /etc/dnsmasq.d/090_wlan0.conf
# sudo cp config/dhcpcd.conf /etc/dhcpcd.conf
# sudo cp config/config.php /var/www/html/includes/
# sudo cp config/defaults.json /etc/raspap/networking/

# sudo systemctl stop systemd-networkd
# sudo systemctl disable systemd-networkd
# sudo cp config/raspap-bridge-br0.netdev /etc/systemd/network/raspap-bridge-br0.netdev
# sudo cp config/raspap-br0-member-eth0.network /etc/systemd/network/raspap-br0-member-eth0.network

# sudo sed -i -E 's/^session\.cookie_httponly\s*=\s*(0|([O|o]ff)|([F|f]alse)|([N|n]o))\s*$/session.cookie_httponly = 1/' /etc/php/7.0/cgi/php.ini
# sudo sed -i -E 's/^;?opcache\.enable\s*=\s*(0|([O|o]ff)|([F|f]alse)|([N|n]o))\s*$/opcache.enable = 1/' /etc/php/7.0/cgi/php.ini
# sudo phpenmod opcache

# echo "net.ipv4.ip_forward=1" | sudo tee /etc/sysctl.d/90_raspap.conf > /dev/null
# sudo sysctl -p /etc/sysctl.d/90_raspap.conf
# sudo /etc/init.d/procps restart

# sudo iptables -t nat -A POSTROUTING -j MASQUERADE
# sudo iptables -t nat -A POSTROUTING -s 192.168.50.0/24 ! -d 192.168.50.0/24 -j MASQUERADE
# sudo iptables-save | sudo tee /etc/iptables/rules.v4

# sudo systemctl unmask hostapd.service
# sudo systemctl enable hostapd.service

# sudo apt-get install -y openvpn
# sudo sed -i "s/\('RASPI_OPENVPN_ENABLED', \)false/\1true/g" /var/www/html/includes/config.php
# sudo systemctl enable openvpn-client@client

# sudo mkdir /etc/raspap/openvpn/
# sudo cp installers/configauth.sh /etc/raspap/openvpn/
# sudo chown -c root:root /etc/raspap/openvpn/*.sh
# sudo chmod 750 /etc/raspap/openvpn/*.sh

# sudo systemctl reboot
