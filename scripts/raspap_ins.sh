# sudo apt-get update
# sudo apt-get full-upgrade
# sudo apt-get install dhcpcd5 lighttpd hostapd dnsmasq iptables-persistent vnstat qrencode php7.0-cgi jq isoquery 

# sudo lighttpd-enable-mod fastcgi-php
# sudo service lighttpd force-reload
# sudo systemctl restart lighttpd.service

# sudo rm -rf /var/www/html
# sudo git clone -b 2.8.7 --depth=1 https://github.com/RaspAP/raspap-webgui /var/www/html

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

# sudo chown -c root:root /etc/raspap/hostapd/*.sh
# sudo chmod 750 /etc/raspap/hostapd/*.sh

# sudo cp installers/configport.sh /etc/raspap/lighttpd
# sudo chown -c root:root /etc/raspap/lighttpd/*.sh

# sudo mv installers/raspapd.service /lib/systemd/system
# sudo systemctl daemon-reload
# sudo systemctl enable raspapd.service

# sudo mv /etc/default/hostapd ~/default_hostapd.old
# sudo cp config/hostapd.conf /etc/hostapd/hostapd.conf
# sudo cp config/090_raspap.conf /etc/dnsmasq.d/090_raspap.conf
# sudo cp config/090_wlan0.conf /etc/dnsmasq.d/090_wlan0.conf
# sudo cp config/dhcpcd.conf /etc/dhcpcd.conf
# sudo cp config/config.php /var/www/html/includes/
# sudo cp config/defaults.json /etc/raspap/networking/

sudo systemctl stop systemd-networkd
sudo systemctl disable systemd-networkd
sudo cp config/raspap-bridge-br0.netdev /etc/systemd/network/raspap-bridge-br0.netdev
sudo cp config/raspap-br0-member-eth0.network /etc/systemd/network/raspap-br0-member-eth0.network
