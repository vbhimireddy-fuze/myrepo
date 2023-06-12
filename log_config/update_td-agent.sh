#!/bin/bash

IPADDRESS=$(ifconfig eth0 | grep inet | grep -v inet6 | tr -s ' ' | cut -d ' ' -f3)

sed -i -e "s/IP_ADDRESS_UNKNOWN/${IPADDRESS}/g" /etc/td-agent/conf.d/worker_0/barcode.conf
td-agent
