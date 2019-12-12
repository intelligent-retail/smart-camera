#!/bin/bash -e

DECOR=----------------
BRIGHT_YELLOW='\u001b[33;1m'
BRIGHT_GREEN='\u001b[32;1m'
BRIGHT_RED='\u001b[31;1m'
BRIGHT_CYAN='\u001b[36;1m'
END_LINE='\033[0m'

if [ ! $(which az) ] 
then 
    echo -e "$BRIGHT_RED\
$DECOR ERROR: az cli not found. Please follow README.md carefully to setup enviroment $DECOR$END_LINE"
    exit 1 # terminate and indicate error
fi

sleep 1

if [ ! $(which python3) ] 
then 
    echo -e "$BRIGHT_YELLOW\
$DECOR WARNING: python3 not found. Try to install python3... $DECOR$END_LINE"
    sudo apt-get install python3
    if  [ $? -ne "0"]
    then 
        echo -e "$BRIGHT_RED\
$DECOR ERROR: Setup python3 failed $DECOR$END_LINE"
        exit 1
    fi
fi

sleep 1

if [ ! $(which pip3) ]
then 
    echo -e "$BRIGHT_YELLOW\
$DECOR WARNING: pip3 not found. Try to install pip3... $DECOR$END_LINE"
    sudo apt-get install python3-pip -y
    if [ $? -ne "0" ]
    then
        echo -e "$BRIGHT_RED\
$DECOR ERROR: Setup pip3 failed $DECOR$END_LINE"
        exit 1
    fi
fi

sleep 1

if [ ! $(which docker) ] 
then
    echo -e "$BRIGHT_YELLOW\
$DECOR WARNING: Docker not found. Try to install docker... $DECOR$END_LINE"
    sudo curl -sSL get.docker.io | bash -
    if [ $? -ne "0" ]
    then
        echo -e "$BRIGHT_RED\
$DECOR ERROR: Setup docker failed $DECOR$END_LINE"
        exit 1
    fi
fi

sleep 1

if [ ! $(which docker-compose) ] 
then 
    echo -e "$BRIGHT_YELLOW\
$DECOR WARNING: docker-compose not found. Try to install docker-compose... $DECOR$END_LINE"
    sudo pip3 install docker-compose
    if  [ $? -ne "0" ]
    then
        echo -e "$BRIGHT_RED\
$DECOR ERROR: Setup docker-compose failed $DECOR$END_LINE"
        exit 1
    fi
fi


