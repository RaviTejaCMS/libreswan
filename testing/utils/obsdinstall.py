#!/bin/python
import pexpect
import sys
import time
import subprocess
KVM_BSD_BASE_NAME = str(sys.argv)
def es(child,expect,send,t=30):
	try:
		child.expect(expect,timeout=t)
		child.send(send+'\n')
	except:
		print("==> Error Executing "+send+" Command <==")
		print("==> Error <==\n"+child.before+'\n ===================')
'''def east():
    if(check("openbsdbase.qcow2")):
        os.system('sudo virsh define east.xml')
        os.system("sudo cp "+POOL+"openbsdbase.qcow2 "+POOL+"obsde.qcow2")
        print("OpenBSD East Created Succesfully")
def west():
    if(check("openbsdbase.qcow2")):
        os.system('sudo virsh define west.xml')
        os.system("sudo cp "+POOL+"openbsdbase.qcow2 "+POOL+"obsdw.qcow2")
        print("OpenBSD West Created Succesfully")

def nfs():
	print("==> Checking if NFS Entries are present")
	if(os.system("showmount -e | grep 192.1.2.* ") != 0):
		os.system('showmount -e 192.168.2.0/24:' + TESTING_DIR)'''

try:
    child = pexpect.spawnu("sudo virsh --connect qemu:///system console --force "+KVM_BSD_BASE_NAME,encoding='utf-8')
    child.expect('boot>')
except:
    print("==> Error Conecting to the Shell <==")
    print(child.before)
    print('==> Exiting the program...!')
    sys.exit(0)
child.logfile = sys.stdout
#sleep for 10 seconds approx so that all those initial boot log loads - Optional
time.sleep(10)
#REGx for Installation prompt
#To enter Shell mode
es(child,'.*hell?','S')
#Expect prompt
#Mounting of drive where install.conf file is present
es(child,'# ','mount /dev/cd0c /mnt')
#Copying of install.conf file
es(child,'# ','cp /mnt/install.conf /')
es(child,'#','cp /mnt/rc.firsttime /')
es(child,'# ','umount /mnt')
#Installing by taking deafult params from install.conf file
es(child,'# ','install -af /install.conf')
es(child,'.*bsd-base# ','mv rc.firsttime /mnt/etc/',150)
es(child,'.*bsd-base# ','echo "iked_flags=YES" >> /mnt/etc/rc.conf.local')
print('====> Shutting Down Base Domain <====')
es(child,'.*bsd-base# ','halt -p\n')
#This is because OpenBSD machine is not getting shutdown :/
time.sleep(10)
child.close()
os.system('sudo virsh destroy '+KVM_BSD_BASE_NAME)