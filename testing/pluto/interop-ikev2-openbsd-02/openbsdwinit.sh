# note swan-prep does not yet supprt iked 
#/testing/guestbin/swan-prep
cp openbsdw.conf /etc/iked.conf
chmod 600 /etc/iked.conf
/sbin/iked
echo "initdone"
