#!/bin/bash -e

source .connectionstring

DECOR=----------------
BRIGHT_CYAN='\u001b[36;1m'
BRIGHT_GREEN='\u001b[32;1m'
BRIGHT_RED='\u001b[31;1m'
END_LINE='\033[0m'

sudo bash -c 'echo "VIDEO_SOURCE_ADDRESS=tcp://video-manager:5562" > /opt/intel/inference_engine_vpu_arm/video_source_config.txt'


if sudo pip3 install getmac
then
    MAC_ADDRESS=$(python3 get_mac_address.py)
    sudo bash -c "echo 'MAC_ADDRESS=$MAC_ADDRESS' > /opt/intel/inference_engine_vpu_arm/camera_id.txt"
else 
    echo -e "$BRIGHT_RED\
$DECOR ERROR: Can't get MAC ADDRESS $DECOR$END_LINE"
    exit 1
fi


echo -e "$BRIGHT_CYAN\
$DECOR Processing: Create folder to contain videos file $DECOR$END_LINE"

backup_and_create_directory(){
    dir_name=$1
    if [ -f "$dir_name" ]; then
        echo -e "$BRIGHT_GREEN File $dir_name already exists, not a directory. \
Backup this file and create a folder videos...$END_LINE"
        mv "$dir_name" "$dir_name".bak
    fi
    mkdir -p "$dir_name"/{output,input}
}

backup_and_create_directory "/home/pi/Desktop/videos"

echo -e "$BRIGHT_GREEN\
$DECOR SUCCESS: Create folder videos with path: $dir_name $DECOR$END_LINE"


echo -e "$BRIGHT_CYAN\
$DECOR PROCESSING: Install docker $DECOR$END_LINE"

if [ $(which docker) ]
then
echo -e "$BRIGHT_GREEN\
$DECOR SUCCESS: Already install docker $DECOR$END_LINE"
else 
    curl -L https://aka.ms/moby-engine-armhf-latest -o moby_engine.deb && sudo dpkg -i ./moby_engine.deb
    curl -L https://aka.ms/moby-cli-armhf-latest -o moby_cli.deb && sudo dpkg -i ./moby_cli.deb
    sudo apt-get install -f
echo -e "$BRIGHT_GREEN\
$DECOR SUCCESS: Install docker $DECOR$END_LINE"
fi

echo -e "$BRIGHT_CYAN\
$DECOR PROCESSING: Install Edge runtime $DECOR$END_LINE"

if [ ! -f "./libiothsm-std.deb" ] && [ ! -f "./iotedge.deb" ]
then 
curl -L https://aka.ms/libiothsm-std-linux-armhf-latest -o libiothsm-std.deb
curl -L https://aka.ms/iotedged-linux-armhf-latest -o iotedge.deb
fi

sudo dpkg -i ./libiothsm-std.deb && sudo dpkg -i ./iotedge.deb
sudo apt-get install -f
sed -i 's|<ADD DEVICE CONNECTION STRING HERE>|'${EDGE_DEVICE_CS}'|g' config.yaml
sudo mv /etc/iotedge/config.yaml /etc/iotedge/config.yaml.bak
sudo cp config.yaml /etc/iotedge/config.yaml

echo -e "$BRIGHT_CYAN\
$DECOR PROCESSING: Restart iotedge.service $DECOR$END_LINE"

sleep 5s
if sudo systemctl restart iotedge
then
echo -e "$BRIGHT_GREEN \
The id (camID) of this device is:

    $MAC_ADDRESS

Please save this id, since you will need it to set up your dashboard server.$END_LINE"

    echo -e "$BRIGHT_GREEN\
$DECOR SUCCESS: Setup the environment on Edge Device $DECOR$END_LINE"
else
    echo -e "$BRIGHT_RED\
$DECOR ERROR: Setup the environment on Edge Device Failed. Please run again! $DECOR$END_LINE"
fi
