obj-m := hw4secws.o
hw4secws-objs := firewall.o ruleio.o logs.o conns.o

ccflags-y := -std=gnu99 -Wall -Wno-declaration-after-statement

all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean