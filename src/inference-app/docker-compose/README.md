# Test app :: micro-services applied

## Preparation

Remember to correct your base image by pointing [video-manager](./video-manager/Dockerfile)
and [ncs2-manager](./ncs2-manager/Dockerfile) and [inference-engine](./inference-engine/Dockerfile)
Dockerfiles to pre-built openvino base image. Then do the following steps
to create and run micro-service version of the test app.

## Build and run

** Remember install your own `inference_engine_vpu_arm`. By default we assumed
OpenVINO will be installed in to `/opt/intel/inference_engine_vpu_arm`. Modify [.env#L4](docker-compose/.env#L4) if you
installed it somewhere else.

### [dot] env content

- [.env](.env)
- [video-manager/.env](./video-manager/.env)
- [ncs2-manager/.env](./ncs2-manager/.env)
- [inference-engine/.env](./inference-engine/.env)

~~~bash
# Example .env file
AWL_DIR=/awl
XSOCK=/tmp/.X11-unix
XAUTH=/tmp/.docker.xauth
INTEL_OPENVINO_DIR=/opt/intel/inference_engine_vpu_arm
~~~

### Headless mode

~~~bash
# Adds docker to X server access control list (ACL)
$ xhost + local:docker

# Build and run the services
$ docker-compose up --build

# Removes docker out of X server ACL if you are not working with
$ xhost - local:docker
 ~~~

### X11 forwarding mode

- Modify [.env](.env) file

~~~bash
SHOW_GUI=True
~~~


- Setup X11

~~~bash
$ XSOCK=/tmp/.X11-unix
$ XAUTH=/tmp/.docker.xauth
$ touch ${XAUTH}
$ xauth nlist ${DISPLAY} | sed 's/^..../ffff/' | xauth -f ${XAUTH} nmerge -
~~~

- Starting the docker container

~~~bash
# Adds docker to X server access control list (ACL)
$ xhost + local:docker

# Build and run the services
$ docker-compose up --build

# Removes docker out of X server ACL if you are not working with
$ xhost - local:docker
 ~~~

## Follow this link about how to config Azure Portal to view data were sent from Edge Device

`https://docs.microsoft.com/en-us/azure/stream-analytics/stream-analytics-quick-create-portal`

## Follow this link about how to instal and manage IoT Edge

`https://docs.microsoft.com/en-us/azure/iot-edge/how-to-install-iot-edge-linux-arm`