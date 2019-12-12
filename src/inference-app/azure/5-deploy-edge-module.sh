#!/bin/bash -e

source .deploy.env
source edge-runtime/.connectionstring
source 0-setup-pc-enviroment.sh

echo -e "$BRIGHT_CYAN\
$DECOR PROCESSING: Deploy module to Azure IoT Hub $DECOR$END_LINE"

ACR_PW=$(az acr credential show -n $ACR_NAME --query "passwords[0].value")

sed -e "s|<myAcrName>|$ACR_NAME|" \
    -e "s|\"password\".*|\"password\": $ACR_PW, |" \
    -e "s|<MY_ZMQ_ADDRESS_IE>|$ZMQ_ADDRESS_IE|" \
    -e "s|<MY_ZMQ_VIDEO_ADDRESS_SUB_IE>|$ZMQ_VIDEO_ADDRESS_SUB_IE|" \
    -e "s|<MY_AZ_CONNECTION_STRING>|$EDGE_DEVICE_CS|" \
    -e "s|<MY_VIDEO_CONFIG_PATH>|$VIDEO_CONFIG_PATH|" \
    -e "s|<MY_MAC_ADDRESS_PATH>|$MAC_ADDRESS_PATH|" \
    -e "s|<MY_IOTHUB_SENDING_INTERVAL>|$IOTHUB_SENDING_INTERVAL|" \
    -e "s|<MY_MAX_DISAPPEARED>|$MAX_DISAPPEARED|" \
    -e "s|<MY_THREAD_SENDING_INTERVAL_VIDEO_ADDRESS>|$THREAD_SENDING_INTERVAL_VIDEO_ADDRESS|" \
    -e "s|<MY_INITIAL_H>|$INITIAL_H|" \
    -e "s|<MY_INITIAL_W>|$INITIAL_W|" \
    -e "s|<MY_QT_X11_NO_MITSHM>|$QT_X11_NO_MITSHM|" \
    -e "s|<MY_SHOW_GUI>|$SHOW_GUI|" \
    -e "s|<MY_XAUTH>|$XAUTH|" \
    -e "s|<MY_XSOCK>|$XSOCK|" \
    -e "s|<MY_ZMQ_ADDRESS_PUB>|$ZMQ_ADDRESS_PUB|" \
    -e "s|<MY_ZMQ_ADDRESS_SUB>|$ZMQ_ADDRESS_SUB|" \
    -e "s|<MY_ZMQ_VIDEO_ADDRESS_SUB_NCS>|$ZMQ_VIDEO_ADDRESS_SUB_NCS|" \
    -e "s|<MY_ZMQ_VIDEO_ADDRESS_REQ_NCS>|$ZMQ_VIDEO_ADDRESS_REQ_NCS|" \
    -e "s|<MY_INTEL_OPENVINO_DIR>|$INTEL_OPENVINO_DIR|" \
    -e "s|<MY_PERSON_DETECTION_THRESHOLD>|$PERSON_DETECTION_THRESHOLD|" \
    -e "s|<MY_FACE_DETECTION_THRESHOLD>|$FACE_DETECTION_THRESHOLD|" \
    -e "s|<MY_THREAD_GET_INTERVAL_VIDEO_ADDRESS>|$THREAD_GET_INTERVAL_VIDEO_ADDRESS|" \
    -e "s|<MY_BUFFER_LESS>|$BUFFER_LESS|" \
    -e "s|<MY_VIDEO_SRC>|$VIDEO_SRC|" \
    -e "s|<MY_ZMQ_VIDEO_ADDRESS_REP>|$ZMQ_VIDEO_ADDRESS_REP|" \
    -e "s|<MY_FRAME_INTERVAL>|$FRAME_INTERVAL|" \
    -e "s|<MY_THREAD_REPLY_VIDEO_FRAME>|$THREAD_REPLY_VIDEO_FRAME|" \
    arm_templates/deployment_edge_module/deployment_edge_module.json \
| az iot edge set-modules --device-id $DEVICE_ID --hub-name $HUB_NAME --content @-

echo -e "$BRIGHT_GREEN\
$DECOR SUCCESS: Deploy module to Azure IoT Hub $DECOR$END_LINE"