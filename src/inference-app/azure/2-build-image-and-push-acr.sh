#!/bin/bash -e

source .deploy.env
source 0-setup-pc-enviroment.sh

cd ../

UNAME_M=$(uname -m)
if [ "${UNAME_M}" = "x86_64" ] && [ ! -f "qemu-arm-static" ]
then
    ./qemu_install.sh
fi

# Build base docker images
if docker build -t raspbian:openvino .
then
    echo -e "$BRIGHT_GREEN\
$DECOR SUCCESS: Build Base Image $DECOR$END_LINE"
else
    echo -e "$BRIGHT_RED\
$DECOR ERROR: Build Base Image Faile, please run again $DECOR$END_LINE"
    exit 1 # terminate and indicate error
fi

# Build 3 docker images
cd docker-compose

if docker-compose build
then
    echo -e "$BRIGHT_GREEN\
$DECOR SUCCESS: Build Three Image $DECOR$END_LINE"
else
    echo -e "$BRIGHT_RED\
$DECOR ERROR: Build Three Image Faile, please run again $DECOR$END_LINE"
    exit 1 # terminate and indicate error
fi

echo -e "$BRIGHT_CYAN\
$DECOR PROCESSING: Push Three Image to Azure Container Registry $DECOR$END_LINE"

# Login to Azure Container Registry
az acr login -n $ACR_NAME
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer --output tsv)


docker tag ncs2-manager:v1 $ACR_LOGIN_SERVER/ncs2-manager:v1
docker push $ACR_LOGIN_SERVER/ncs2-manager:v1

docker tag video-manager:v1 $ACR_LOGIN_SERVER/video-manager:v1
docker push $ACR_LOGIN_SERVER/video-manager:v1

docker tag inference-engine:v1 $ACR_LOGIN_SERVER/inference-engine:v1
docker push $ACR_LOGIN_SERVER/inference-engine:v1

echo -e "$BRIGHT_GREEN\
$DECOR SUCCESS: Push Three Image to Azure Container Registry $DECOR$END_LINE"