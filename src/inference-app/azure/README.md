# Auto deploy Azure IoT

## Prerequisites

- Development machine(Personal Computer) with OS is Linux Ubuntu 18.04
- Raspberry Pi 3B+ with OS is Raspian Stretch
    - micro SD card 32GB A1 V30
    - Movidius NCS2 (or NCS1)
    - PiCamera v2.1

## Development machine setup

### Install [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-apt?view=azure-cli-latest) in Development machine

```bash
# Install Azure CLI
$ curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to your Azure Account
$ az login

# Add Microsoft Azure IoT Extension for Azure CLI
$ az extension add --name azure-cli-iot-ext
```

### Clone this repository & Install the essential softwares

\* Working directory: `<repository_root_dir>/src/inference-app/azure`

```bash
$ ./0-setup-pc-enviroment.sh
```

- If it's the first time you installed Docker on the development PC, for using `docker` command without sudo, you need to add the current user to the docker group:
```bash
$ sudo usermod -aG docker $(whoami)
```

## Raspberry Pi setup

### Hardware setup

- Download Raspbian Stretch image:
http://downloads.raspberrypi.org/raspbian/images/raspbian-2019-04-09/

- Download etcher tool and install on development machine:
https://www.balena.io/etcher/

- Follow this link to burn the image on SD card:
https://www.raspberrypi.org/documentation/installation/installing-images/

- Plug PiCamera, Movidius NCS2, micro SD card into Raspberry Pi and turn-on it:
    - In the first time, we need to choose some option for Raspbian OS
    - We must enable SSH, PiCamera and VNC (optional)

- If you can't access to your Raspberry Pi directly:
    - Create a file named `ssh` in the boot partition of your SD card to enable SSH connection (see the [official documentation](https://www.raspberrypi.org/documentation/remote-access/ssh/) for details).
    - Run `sudo raspi-config` to setup the initial settings and enable the PiCamera and VNC (optional).

### Library setup

- Download [OpenVINO](https://download.01.org/opencv/2019/openvinotoolkit/R1/l_openvino_toolkit_raspbi_p_2019.1.094.tgz) to your Raspberry Pi
- Unpack the archive to the expected location (`/opt/intel/inference_engine_vpu_arm`):
    ```bash
    $ tar xzf l_openvino_toolkit_raspbi_p_<version>.tgz
    $ sudo mkdir /opt/intel/ && sudo mv inference_engine_vpu_arm /opt/intel/
    ```
- Run these commands to setup the camera configurations:
    ```bash
    $ sudo /bin/bash -c 'echo "bcm2835-v4l2"  >> /etc/modules'
    $ sudo reboot
    ```

## Deploy Azure Resources and Edge Modules

### Create Azure Resources (on your development PC)

- Modify [env](.deploy.env#L1) parameters to setup Azure Resource:
```
RESOURCE_GROUP=
LOCATION=
ACR_NAME=
HUB_NAME=
DEVICE_ID=
```

- Run scripts \#1~\#3:
```bash
# Setup Azure Rersource (Resource Group, Container Registry, IoT Hub)
$ ./1-deploy-azure-resources.sh

# Build Image and push to Azure Container Registry
$ ./2-build-image-and-push-acr.sh

# Register Edge Device on Azure IoT Hub
$ ./3-register-edge-device.sh
```

### Setup edge device (on Raspberry Pi)

- Copy folder `edge-runtime` to your edge device and run script \#4 inside of it:

```bash
# Setup Docker and IoT Edge Runtime for Raspberry Pi
$ ./4-setup-edge-device.sh
```

- Remember to save the `camID` when the script is finished successfully (you will need it later)
- When the script is finish, folder `videos` to contain video files will be created on Raspberry Pi Desktop (`/home/pi/Desktop/videos`)

### Deploy edge module to Azure IoT Hub (on your development PC)

- Modify [env](.deploy.env#L50) to setup Video Resource (Default is use [PiCamera mode](.deploy.env#L52), and video 1 min file will write in `/home/pi/Desktop/videos/output`)
- When you choice [Video files mode](.deploy.env#L61), please add your video files in `/home/pi/Desktop/videos/input`
- Run script \#5 to deploy edge modules to Azure IoT Hub (it may take some time to start all the modules on the edge device):
```bash
# Deploy edge module to Azure IoT Hub
$ ./5-deploy-edge-module.sh
```

#### For removing modules from Azure IoT Hub

- Run script \#6 (on your development PC)

```bash
# Delete module from Azure Iot Hub
$ ./6-delete-edge-module.sh
```
