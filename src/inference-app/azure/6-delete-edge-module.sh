#!/bin/bash -e

source .deploy.env
source edge-runtime/.connectionstring
source 0-setup-pc-enviroment.sh

echo -e "$BRIGHT_CYAN\
$DECOR PROCESSING: Delete module Azure IoT Hub $DECOR$END_LINE"

ACR_PW=$(az acr credential show -n $ACR_NAME --query "passwords[0].value")

STOP_MODULE_PATH="stop-module.json"
sed -e "s|<myAcrName>|$ACR_NAME|" \
    -e "s|\"password\".*|\"password\": $ACR_PW, |" \
    arm_templates/delete_edge_module/delete_edge_module.json \
| az iot edge set-modules --device-id $DEVICE_ID --hub-name $HUB_NAME --content @-

echo -e "$BRIGHT_GREEN\
$DECOR SUCCESS: Delete module Azure IoT Hub $DECOR$END_LINE"