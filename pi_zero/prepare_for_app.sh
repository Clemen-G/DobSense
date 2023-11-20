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

print_header "Patching /boot/cmdline.txt"
sed -i 's/rootwait quiet/rootwait modules-load=dwc2,g_ether quiet/' /boot/cmdline.txt


print_header "Patching /boot/config.txt"

CONFIG_FILE="/boot/config.txt"

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

echo "Adding dwc2 to dtoverlay"

if grep -q "^dtoverlay=" $CONFIG_FILE; then
    sed -i '/dwc2/!s/^dtoverlay=.*/&,dwc2/' $CONFIG_FILE
else
    echo "dtoverlay=dwc2" | tee -a $CONFIG_FILE
fi


print_header "Disabling unneeded services"

for srv in lightdm cups-browsed cups ModemManager; do
    echo "Disabling system service $srv"
    systemctl disable $srv
    systemctl stop $srv
done

for srv in pulseaudio pipewire pipewire-pulse; do
    echo "Disabling user service $srv"
    su $SUDO_USER -c "systemctl --user mask $srv.socket"
    su $SUDO_USER -c "systemctl --user mask $srv.service"
done


print_header "Installing Docker"

apt-get update
apt-get install ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository to Apt sources:
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update

apt-get install docker-ce docker-ce-cli containerd.io 


print_header "Access Point configuration"

nmcli con add type wifi ifname wlan0 mode ap con-name Nushscope ssid Nushscope
nmcli con modify Nushscope 802-11-wireless.band bg
nmcli con modify Nushscope 802-11-wireless.cloned-mac-address permanent
nmcli con modify Nushscope ipv4.method manual ipv4.address 192.168.99.1/24
nmcli con modify Nushscope ipv6.method disabled

# Todo: should I remove authentication altogether?
nmcli con modify Nushscope wifi-sec.key-mgmt wpa-psk
nmcli con modify Nushscope wifi-sec.psk "password"

print_header "Installing and configuring DHCP server"

apt install -y dnsmasq
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
    docker run --memory 256M --publish 192.168.99.1:443:8000 --detach nushscope_arm64
fi
EOF


cat <<'EOF' > /etc/system.d/system/ConfigureMode.service
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