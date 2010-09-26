#!/bin/sh

exitcode=1

# cd /opt/xibo/pyclient/client/python

while [ $exitcode -ne 0 ]
do
	/usr/bin/python XiboClient.py
	exitcode=${?}
done
