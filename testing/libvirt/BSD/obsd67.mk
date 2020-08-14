KVM_ISO_URL_BSD = https://cloudflare.cdn.openbsd.org/pub/OpenBSD/6.7/amd64/install67.iso
KVM_ISO_URL_BSD = https://cdn.openbsd.org/pub/OpenBSD/6.7/amd64/install67.iso
KVM_BSD_RC = testing/libvirt/rc.firsttime
KVM_BSD_CONF = testing/libvirt/install.conf
KVM_BSD_ISO = install67.iso
KVM_BSD_BASE_NAME = openbsd-base
#We install OpenBSD 6.7 but use os-varient as openbsd6.6 as virt install dosen't support 6.7 yet :(
VIRT_BSD_VARIANT = openbsd6.6
define kvm-clean-obsd
	tmp=$(virsh list --all | grep " $1 ")
	if [ -z "$tmp" ]
	then
		echo "$1 Domain doesn't Exist"
		return 0
	else
		echo "Undefining $1"
		sudo virsh undefine $1
	fi
endef

define kvm-obsd-create
	if [[ -f "$(KVM_POOLDIR)/$(KVM_BSD_ISO)" ]]; then \
	    echo "$(KVM_BSD_ISO) exists in Pool directory" \ 
	else 
	    echo "ISO does not exist Dowloading the file"
		wget --output-document $KVM_BSD_ISO.tmp --no-clobber -- $(KVM_ISO_URL_BSD) -P $(KVM_POOLDIR)
		mv $KVM_BSD_ISO.tmp $KVM_BSD_ISO
	fi
	if [[ -z $(call kvm-clean-obsd $(KVM_BSD_BASE_NAME)) ]]
	then
	   echo "VM does not exist "
	   $(call kvm-base-obsd)
	else
	    echo "VM is running!"
		echo "Undefining VM"
	fi
endef
define kvm-base-obsd
		sed -e "s:@@TESTINGDIR@@:$$(KVM_TESTINGDIR):" rc.firsttime > $(KVM_POOLDIR)/rc.firsttime
		cp install.conf boot.conf $(KVM_POOLDIR)/
		sudo env -i growisofs -M "$(KVM_POOLDIR)/install67.iso" -l -R -graft-points /install.conf="$(KVM_POOLDIR)/install.conf" /etc/boot.conf="$(KVM_POOLDIR)/boot.conf" /rc.firsttime="$(KVM_POOLDIR)/rc.firsttime"
		sudo virt-install --name=$(KVM_BSD_BASE_NAME) --virt-type=kvm --memory=2048,maxmemory=2048 \
        --vcpus=1,maxvcpus=1 --cpu host --os-variant=$(VIRT_BSD_VARIANT) \
        --cdrom=$(KVM_POOLDIR)/install67.iso \
        $(VIRT_GATEWAY) \
        --disk path=$(KVM_POOLDIR)/$(KVM_BSD_BASE_NAME).qcow2,size=4,bus=virtio,format=qcow2 \
        --graphics none --serial pty
		$(KVM_PYTHON) $(KVM_TESTINGDIR)/utils/obsdinstall.py $(KVM_BSD_BASE_NAME)
	#This should be continued for east and wet too to write that also sed for east and west
endef
