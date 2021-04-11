/testing/guestbin/swan-prep --x509
certutil -d sql:/etc/ipsec.d -D -n "Libreswan test CA for mainca - Libreswan"
ipsec start
../../guestbin/wait-until-pluto-started
ipsec whack --impair send-pkcs7-thingie
ipsec auto --add westnet-eastnet-x509
ipsec auto --status | grep westnet-eastnet-x509
echo "initdone"
