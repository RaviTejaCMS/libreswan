/testing/guestbin/swan-prep
ipsec start
../../guestbin/wait-until-pluto-started
ipsec whack --impair ke-payload:omit
ipsec auto --add westnet-eastnet-ipv4-psk-ikev2
echo "initdone"
