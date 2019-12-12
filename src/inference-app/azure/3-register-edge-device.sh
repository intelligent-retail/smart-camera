#!/bin/bash -e

source .deploy.env
source 0-setup-pc-enviroment.sh

echo -e "$BRIGHT_CYAN\
$DECOR PROCESSING: Register Edge Device $DECOR$END_LINE"

if az iot hub device-identity create --device-id ${DEVICE_ID} \
    --hub-name ${HUB_NAME} --edge-enabled

then
HUB_CS=$(az iot hub show-connection-string \
            --name $HUB_NAME --query "connectionString")
EDGE_DEVICE_CS=$(az iot hub device-identity show-connection-string \
                    -d $DEVICE_ID -n $HUB_NAME --query "connectionString")
echo "HUB_CS=$HUB_CS" > edge-runtime/.connectionstring
echo "EDGE_DEVICE_CS=$EDGE_DEVICE_CS" >> edge-runtime/.connectionstring
echo -e "$BRIGHT_GREEN $DECOR \
SUCCESS: Register EdgeDevice $DEVICE_ID. Please copy folder edge-runtime into \
your RaspPi and run script 4-setup-edge-device.sh! $DECOR$END_LINE"

else  echo -e "$BRIGHT_RED\
$DECOR ERROR: Register Edge Device Failed $DECOR$END_LINE" && exit

fi
