#!/usr/bin/env bash

# Quits the script if any command fails
set -e

print_header() {
    local message="$1"
    echo
    echo '=============================='
    echo "$message"
    echo '=============================='
    echo
}


CONFIG_FILE="/boot/firmware/config.txt"

print_header "Patching $CONFIG_FILE"

echo "Ensuring dtparam=audio=off"
sed -i 's/^dtparam=audio=on/dtparam=audio=off/' $CONFIG_FILE

echo "Ensuring camera_auto_detect=0"
sed -i '/^camera_auto_detect=1/c\camera_auto_detect=0' $CONFIG_FILE

echo "Ensuring display_auto_detect=0"
sed -i '/^display_auto_detect=1/c\display_auto_detect=0' $CONFIG_FILE

echo "Commenting out dtoverlay=vc4-kms-v3d"
sed -i '/^dtoverlay=vc4-kms-v3d/s/^/#/' $CONFIG_FILE

echo "Ensuring gpu_mem=16"
# This checks if gpu_mem is already set, and if not, adds it
if grep -q "^gpu_mem=" $CONFIG_FILE; then
    sed -i '/^gpu_mem=/c\gpu_mem=16' $CONFIG_FILE
else
    echo "gpu_mem=16" | tee -a $CONFIG_FILE
fi


print_header "Enabling USB Ethernet"

CMDLINE="/boot/firmware/cmdline.txt"
echo "Patching $CMDLINE"

if ! grep -q "modules-load=dwc2,g_ether" $CMDLINE; then
    sed -i 's/rootwait /rootwait modules-load=dwc2,g_ether /' $CMDLINE
    echo "Added modules-load=dwc2,g_ether to $CMDLINE"
fi

echo "Adding dwc2 to dtoverlay"

if awk '/^\[pi02\]/{found=1;  next} /^\[.*\]/{found=0; next} found && /^dtoverlay=dwc2/{exit 1}' "$CONFIG_FILE"; then
    echo -e "\n[pi02]\ndtoverlay=dwc2" >> "$CONFIG_FILE"
fi

echo "Ensuring usb gadget is managed, so that it can be activated at startup."
if [ ! -f '/etc/udev/rules.d/85-nm-unmanaged.rules' ]; then
    cp /usr/lib/udev/rules.d/85-nm-unmanaged.rules /etc/udev/rules.d/85-nm-unmanaged.rules
fi
sed 's/^[^#]*gadget/#\ &/' -i /etc/udev/rules.d/85-nm-unmanaged.rules

echo "Checking if usb0 is already configured"
if ! nmcli con | grep -q usb-p2p; then
    IP=192.168.4.100/24
    sudo nmcli con add \
        con-name usb-p2p \
        type ethernet \
        ifname usb0 \
        ipv4.addresses $IP \
        connection.autoconnect yes \
        ipv4.method manual
    echo "Added a new connection for usb0, static IP: $IP"
fi


print_header "Disabling unneeded services"

for srv in lightdm cups-browsed cups ModemManager; do
    srv="${srv}.service"
    if [ -n "$(systemctl list-units -q $srv)" ]; then
        echo "Disabling system service $srv"
        systemctl disable $srv
        systemctl stop $srv
    fi
done

for srv in pulseaudio pipewire pipewire-pulse; do
    srv="${srv}.service"
    if [ -n "$(systemctl list-units -q $srv)" ]; then
        echo "Disabling user service $srv"
        su $SUDO_USER -c "systemctl --user mask $srv.socket"
        su $SUDO_USER -c "systemctl --user mask $srv.service"
    fi
done


print_header "Installing Docker"

echo "Updating package list"
apt-get update -q -y

echo "Installing certificates and tools for docker"
apt-get install -y ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor --yes -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository to Apt sources:
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null


echo "Installing Docker packages"
apt-get install -y docker-ce docker-ce-cli containerd.io 

mkdir -p /var/local/shared_docker

print_header "Access Point configuration"

if [ -z "$(nmcli connection show | grep Nushscope)" ]; then
    nmcli con add type wifi ifname wlan0 mode ap con-name Nushscope ssid Nushscope
    nmcli con modify Nushscope 802-11-wireless.band bg
    nmcli con modify Nushscope 802-11-wireless.cloned-mac-address permanent
    nmcli con modify Nushscope ipv4.method manual ipv4.address 192.168.99.1/24
    nmcli con modify Nushscope ipv6.method disabled
fi

print_header "Installing and configuring DHCP server"

apt-get install -y dnsmasq
systemctl stop dnsmasq
systemctl disable dnsmasq

cat <<EOF > /etc/dnsmasq.d/nushscope.conf
interface=wlan0

# setting explicitly to reduce risk of conflicts if dnsmasq does not terminate
listen-address=192.168.99.1

dhcp-range=192.168.99.2,192.168.99.20,1h

# disables passing default route to dhcp clients
dhcp-option=option:router
EOF


print_header "Installing AP/Tethered mode switcher"

cat <<'EOF' > /usr/sbin/configure_mode.sh
#!/usr/bin/env bash

INTERFACE_NAME="usb0"

if ip link show $INTERFACE_NAME | grep -q "state UP"; then
    echo stopping DHCP server
    systemctl stop dnsmasq

    echo activating default wifi connection
    default_wifi_connection=$(nmcli con show | grep wifi | grep -v Nushscope | cut -d ' ' -f 1)
    nmcli con up $default_wifi_connection
else
    echo configuring access point mode
    nmcli con up Nushscope

    echo starting DHCP server
    systemctl start dnsmasq

    echo starting the container
    docker run --mount type=bind,src=/var/local/shared_docker,target=/shared --publish 443:8443 --publish 80:8080 --detach nushscope_arm64
fi
EOF

chmod u+x /usr/sbin/configure_mode.sh


cat <<'EOF' > /etc/systemd/system/ConfigureMode.service
[Unit]
Description=Configures Nushscope Server/Tethered mode
Requires=NetworkManager-wait-online.service Docker.socket
After=NetworkManager-wait-online.service Docker.socket

[Service]
Type=oneshot
ExecStart=/usr/sbin/configure_mode.sh

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ConfigureMode.service

print_header "Done"