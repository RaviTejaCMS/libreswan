ipsec whack --shutdown
semodule -r ipsecspd
rm -rf ipsecspd.fc ipsecspd.if tmp
