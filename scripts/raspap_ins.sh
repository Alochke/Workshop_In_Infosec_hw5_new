# sudo apt-get update
# sudo apt-get full-upgrade
# sudo apt-get install dhcpcd5 lighttpd hostapd dnsmasq iptables-persistent vnstat qrencode php7.0-cgi jq isoquery 

# sudo lighttpd-enable-mod fastcgi-php
# sudo service lighttpd force-reload
# sudo systemctl restart lighttpd.service

# sudo rm -rf /var/www/html
git clone -b 2.8.7 --depth=1 https://github.com/RaspAP/raspap-webgui /var/www/html
