#!/bin/bash -e
source .deploy.env
source 0-setup-pc-enviroment.sh

echo -e "$BRIGHT_CYAN\
$DECOR PROCESSING: Create Azure Resouce Group $DECOR$END_LINE"
az group create \
  --name ${RESOURCE_GROUP} \
  --location ${LOCATION}


echo -e "$BRIGHT_CYAN\
$DECOR PROCESSING: Create Azure Container Registry $DECOR$END_LINE"
TEMPLATE_ACR_PATH="arm_templates/container_registry/template.json"

sed -e "s/<myLocation>/$LOCATION/" \
    -e "s/<myAcrName>/$ACR_NAME/" \
    arm_templates/container_registry/parameters.json \
| az group deployment create --resource-group $RESOURCE_GROUP \
    --template-file $TEMPLATE_ACR_PATH --parameters @-


echo -e "$BRIGHT_CYAN\
$DECOR PROCESSING: Create Azure IoT Hub $DECOR$END_LINE"
TEMPLATE_IOT_PATH="arm_templates/iot_hub/template.json"

sed -e "s/<myLocation>/$LOCATION/" \
    -e "s/<myHubName>/$HUB_NAME/" \
    arm_templates/iot_hub/parameters.json \
| az group deployment create --resource-group $RESOURCE_GROUP \
    --template-file $TEMPLATE_IOT_PATH --parameters @-

echo -e "$BRIGHT_GREEN\
$DECOR SUCCESS: Deploy Azure Resource $DECOR$END_LINE"
