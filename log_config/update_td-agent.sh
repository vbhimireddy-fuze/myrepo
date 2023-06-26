#!/bin/bash

IPADDRESS=$(ifconfig eth0 | grep inet | grep -v inet6 | tr -s ' ' | cut -d ' ' -f3)
HOSTNAME=$(cat /etc/hostname)

sed -i -e "s/IP_ADDRESS_PLACEHOLDER/${IPADDRESS}/g" /etc/td-agent/td-agent.conf
sed -i -e "s/HOSTNAME_PLACEHOLDER/${HOSTNAME}/g" /etc/td-agent/td-agent.conf
TZ=utc td-agent
