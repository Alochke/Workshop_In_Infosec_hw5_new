sudo rmmod hw4secws
git pull
cd ~/Workshop_In_Infosec_hw5_new/module
make
sudo insmod ~/Workshop_In_Infosec_hw5_new/module/hw4secws.ko
sudo python3.7 ~/Workshop_In_Infosec_hw5_new/user/fwclient.py load_rules ~/Workshop_In_Infosec_hw5_new/user/rules\ example.txt
sudo python3.7 ~/Workshop_In_Infosec_hw5_new/smtp/smtpproxy.py
