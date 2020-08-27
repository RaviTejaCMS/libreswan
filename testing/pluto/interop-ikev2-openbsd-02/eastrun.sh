ipsec auto --up eastnet-westnet-ikev2
ping -n -c 4 -I 192.0.2.254 192.0.1.254
ipsec trafficstatus
# fails
#ipsec auto --up  eastnet-westnet-ikev2-ipv6
echo done
