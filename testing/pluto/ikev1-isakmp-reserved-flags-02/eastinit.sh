/testing/guestbin/swan-prep
ipsec start
../../guestbin/wait-until-pluto-started
ipsec whack --impair send-bogus-isakmp-flag
ipsec auto --add westnet-eastnet
ipsec auto --status | grep westnet-eastnet
echo "initdone"
