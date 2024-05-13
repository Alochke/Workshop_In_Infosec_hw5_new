# sudo apt-get update
# sudo apt-get full-upgrade
# sudo apt-get install dhcpcd5 lighttpd hostapd dnsmasq iptables-persistent vnstat qrencode
# sudo apt-get install php7.0-cgi

bazel build --config=noaws --config=nohdfs --config=nokafka --config=noignite --config=nonccl -c opt --verbose_failures //tensorflow/tools/pip_package:build_pip_package
