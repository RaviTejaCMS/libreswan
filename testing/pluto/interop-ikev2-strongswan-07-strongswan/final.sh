ip xfrm pol
ip xfrm state
if [ -f /var/run/pluto/pluto.pid ]; then ../../pluto/bin/ipsec-look.sh ; fi
if [ -f /var/run/charon.pid -o -f /var/run/strongswan/charon.pid ]; then strongswan statusall ; fi
: ==== cut ====
if [ -f /var/run/pluto/pluto.pid ]; then ipsec auto --status ; fi
if [ -f /var/run/charon.pid -o -f /var/run/strongswan/charon.pid ]; then strongswan statusall ; fi
: ==== tuc ====
../bin/check-for-core.sh
if [ -f /sbin/ausearch ]; then ausearch -r -m avc -ts recent ; fi
: ==== end ====
