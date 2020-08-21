#!/bin/bash
set -e
if grep -qF "192.1.2.0/24" /etc/exports;then
   echo "fstab entry already exists"
else
   echo "@@TESTINGDIR@@ 192.1.2.0/24(rw,no_root_squash)"
fi
sudo systemctl start nfs-server
sudo exportfs -r