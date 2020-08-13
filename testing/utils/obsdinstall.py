#!/bin/python
import pexpect
import sys
import time
import os
import argparse
'''parser = argparse.ArgumentParser(description='To Spin Up OpenBSD Domains')
parser.add_argument("--ISO",required=True)'''
ISO_PATH = 'install67.iso'
VIRSH_NAME="openbsd-base"
ISO_PATH_V="/var/lib/libvirt/boot/install67.iso"
POOL=""
DISK_PATH="/var/lib/libvirt/images/openbsdbase.qcow2"
TESTING_DIR = '/home/testing'
def es(child,expect,send,t=30):
	try:
		child.expect(expect,timeout=t)
		child.send(send+'\n')
	except:
		print("==> Error Executing "+send+" Command <==")
		print("==> Error <==\n"+child.before+'\n ===================')
def check(image):
    return (POOL+image)
def east():
    if(check("openbsdbase.qcow2")):
        os.system('sudo virsh define east.xml')
        os.system("sudo cp "+POOL+"openbsdbase.qcow2 "+POOL+"obsde.qcow2")
        print("OpenBSD East Created Succesfully")
    else:
        base()
        east()
def west():
    if(check("openbsdbase.qcow2")):
        os.system('sudo virsh define west.xml')
        os.system("sudo cp "+POOL+"openbsdbase.qcow2 "+POOL+"obsdw.qcow2")
        print("OpenBSD West Created Succesfully")

def nfs():
	print("==> Checking if NFS Entries are present")
	if(os.system("showmount -e | grep 192.1.2.* ") != 0):
		os.system('showmount -e 192.168.2.0/24:' + TESTING_DIR)
def base():
    #We install OpenBSD 6.7 but use os-varient as openbsd6.6 as virt install dosen't support 6.7 yet :(
    VIRSH_COMMAND = 'sudo virt-install --name='+VIRSH_NAME+' --virt-type=kvm --memory=2048,maxmemory=2048 \
        --vcpus=1,maxvcpus=1 --cpu host --os-variant=openbsd6.6 \
        --cdrom='+ISO_PATH_V+' \
        --network=bridge=virbr0,model=virtio \
        --disk path='+DISK_PATH+',size=4,bus=virtio,format=qcow2 \
        --graphics none --serial pty'
    try:
        child = pexpect.spawnu(VIRSH_COMMAND,encoding='utf-8')
        child.expect('boot>')
    except:
        print("==> Error executing virsh Command <==")
        print(child.before)
        print('==> Exiting the program...!')
        sys.exit(0)
    print("==> Virt Command executed <==")
    child.logfile = sys.stdout
    #sleep for 10 seconds approx so that all those initial boot log loads - Optional
    time.sleep(10)
    #REGx for Installation prompt
    #To enter Shell mode
    es(child,'.*hell?','S')
    #print("\n==> Shell Mode Entered <==")
    #Expect prompt
    #Mounting of drive where install.conf file is present
    es(child,'# ','mount /dev/cd0c /mnt')
    print("==> Mounted <==")
    #Copying of install.conf file
    es(child,'# ','cp /mnt/install.conf /')
    es(child,'#','cp /mnt/rc.firsttime /')
    print("==> install.conf file is copied <==")
    es(child,'# ','umount /mnt')
    #Installing by taking deafult params from install.conf file
    es(child,'# ','install -af /install.conf')
    #child.logfile = sys.stdout
    print("==> Starting Installation <==")
    print('==> Copying necessary Files <==')
    es(child,'.*bsd-base# ','mv rc.firsttime /mnt/etc/',150)
    es(child,'.*bsd-base# ','echo "iked_flags=YES" >> /mnt/etc/rc.conf.local')
    print('====> Shutting Down Base Domain <====')
    es(child,'.*bsd-base# ','halt -p\n')
    #This is because OpenBSD machine is not getting shutdown :/
    time.sleep(10)
    child.close()
    os.system('sudo virsh destroy openbsd-base')
def check():
    pass

#Check if iso exists
if(not os.path.exists(ISO_PATH)):
		print("install67.iso does not exists in this folder")
		sys.exit()
#install.conf file
if(not os.path.exists("install.conf")):
	print("install.conf does not exists in this folder")
	print("Downloading install.conf")
	os.system("wget -O install.conf https://termbin.com/sldb")
#boot.conf file
if(not os.path.exists("boot.conf")):
	print("boot.conf does not exists creting it!")
	os.system('echo -e "set tty com0\nstty com0 115200\nset timeout 1" > boot.conf')
#editing the iso file
os.system('sudo env -i growisofs -M "install67.iso" -l -R -graft-points /install.conf="install.conf" /etc/boot.conf="boot.conf" /rc.firsttime="rc.firsttime"')
#moving file from current directory to ISO_PATH_V from ISO_P
os.system('sudo cp '+ISO_PATH+' '+ISO_PATH_V)