/testing/guestbin/swan-prep
ipsec start
../../guestbin/wait-until-pluto-started
ipsec auto --add east
ipsec whack --impair revival
echo "initdone"
