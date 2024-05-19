#!/bin/bash

telnet 10.1.2.2 25
helo idk
mail from: idk
rcpt to: root
data
$(cat $1)
.