/testing/guestbin/swan-prep
ipsec start
../../guestbin/wait-until-pluto-started
ipsec auto --add westnet-eastnet
ipsec whack --impair suppress-retransmits
echo "initdone"
