# sudo apt-get update
# sudo apt-get full-upgrade
# sudo apt-get install dhcpcd5 lighttpd hostapd dnsmasq iptables-persistent vnstat qrencode
# sudo apt-get install php7.0-cgi

cd ~/Tensorflow-1.13.2/third_party/icu &&
sed -i 's/e15ffd84606323cbad5515bf9ecdf8061cc3bf80fb883b9e6aa162e485aa9761/86b85fbf1b251d7a658de86ce5a0c8f34151027cc60b01e1b76f167379acf181/g' ./workspace.bzl
