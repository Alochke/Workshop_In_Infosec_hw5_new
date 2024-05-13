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
sudo cp installers/raspap.sudoers /etc/sudoers.d/090_raspap