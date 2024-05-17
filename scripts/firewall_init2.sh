sudo rmmod hw4secws
git pull
sudo insmod ~/Workshop_In_Infosec_hw5_new/module/hw4secws.ko
cd ~/Workshop_In_Infosec_hw5_new/module
make
sudo python3.7 ~/Workshop_In_Infosec_hw5_new/user/fwclient.py load_rules ~/Workshop_In_Infosec_hw5_new/user/rules\ example.txt
sudo python3.7 ~/Workshop_In_Infosec_hw5_new/http/CVEmitigation.py
