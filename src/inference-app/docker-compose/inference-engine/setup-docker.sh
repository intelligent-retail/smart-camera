#! /bin/bash

echo -e "\u001b[33;1m\
---------------- Setup Daemon Docker ----------------\033[0m"

if [-f $FILE_NAME ]; then
    mv /etc/docker/daemon.json /etc/docker/daemon.json.bak
fi
cp daemon.json /etc/docker/daemon.json
sleep 2
sudo systemctl restart docker