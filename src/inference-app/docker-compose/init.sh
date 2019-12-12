#!/bin/bash

# Transfer some libs
cp ./utils/zmqutils.py ./video-manager/
cp ./utils/zmqutils.py ./ncs2-manager/
cp ./utils/zmqutils.py ./inference-engine/

# Permit read access
chmod +x ./video-manager/entrypoint.sh
chmod +x ./ncs2-manager/entrypoint.sh
chmod +x ./inference-engine/entrypoint.sh