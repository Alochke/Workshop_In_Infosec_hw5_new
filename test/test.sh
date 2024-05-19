#!/bin/bash

echo "helo idk
mail from: idk
rcpt to: root
data
$(cat $1)
." |telnet 10.1.2.2 25
