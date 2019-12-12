#!/usr/bin/env python3
import os
import sys
import time
import copy
import json
import zmqutils
import logging as log
import threading
from centroidtracker import CentroidTracker
from iothub_client import IoTHubClient, IoTHubTransportProvider
from iothub_client import IoTHubMessage, IoTHubError


log.basicConfig(stream=sys.stdout, level=log.DEBUG)

# Get value from env variable
CONNECTION_STRING = os.getenv("AZ_CONNECTION_STRING", None)
# Using the MQTT protocol.
PROTOCOL = IoTHubTransportProvider.MQTT
# ENV
video_config_path = os.getenv("VIDEO_CONFIG_PATH", "")
cam_id_path = os.getenv("MAC_ADDRESS_PATH", "")
zmq_address = os.getenv("ZMQ_ADDRESS", "tcp://localhost:5960")
zmq_video_address = os.getenv("ZMQ_VIDEO_ADDRESS_SUB", "tcp://*:5561")
sending_interval = int(os.getenv("IOTHUB_SENDING_INTERVAL", "5"))
max_disappeared = os.getenv("MAX_DISAPPEARED", "50")
thread_sending_interval_video_address = int(
    os.getenv("THREAD_SENDING_INTERVAL_VIDEO_ADDRESS", "20")
)

# Define global variable
timestamps = None
timestamps_is_checked = False


def send_confirmation_callback(message, result, user_context):
    print("IoT Hub responded to message with status: %s" % (result))


def iothub_client_init():
    # Create an IoT Hub client
    client = IoTHubClient(CONNECTION_STRING, PROTOCOL)
    return client


def iothub_client_run(json_object):

    try:
        # Build the message with detection result values.
        message = IoTHubMessage(json_object)

        # Send the message.
        client.send_event_async(message, send_confirmation_callback, None)

    except IoTHubError as iothub_error:
        log.error("Unexpected error %s from IoTHub" % iothub_error)
        return
    except KeyboardInterrupt:
        log.error("IoTHubClient sample stopped")


# ZMQ Publisher
pub, pub_ctx = zmqutils.pub(zmq_video_address)
# ZMQ Subscriber
sub, ctx = zmqutils.sub(zmq_address)

# Init a IoT Hub client
client = iothub_client_init()


def get_video_source_from_config_file():
    data = {"video_address": ""}
    try:
        video_address_from_config_file = (
            open(video_config_path).readline().split("=")[1].strip()
        )

    except BaseException:
        # Get defaul value
        video_address_from_config_file = "tcp://video-manager:5562"
        log.info(
            "Error config file!!! Using this default value is {}".format(
                video_address_from_config_file
            )
        )

    data["video_address"] = video_address_from_config_file
    pub.send_json(data, flags=0)
    log.info(
        "Just sent the video source address : {}".format(
            video_address_from_config_file
        )
    )


def get_cam_id_from_config_file():
    try:
        cam_id = open(cam_id_path).readline().split("=")[1].strip()

    except BaseException:
        # Get defaul value
        cam_id = "00:00:00:00:00:00"
        log.info(
            "Error config file!!! Using this default value is {}".format(
                cam_id
            )
        )
    return cam_id


# Get video source at first
get_video_source_from_config_file()

# Get mac address from config file
mac_address = get_cam_id_from_config_file()

# Tracker
ct = CentroidTracker(float(max_disappeared))


def check_point_in_polygon(face_geometry, person_geometry):
    center_face = (
        face_geometry[0] + (face_geometry[2] / 2),
        face_geometry[1] + (face_geometry[3] / 2),
    )
    if (
        center_face[0] > person_geometry[0] and
        center_face[0] < person_geometry[2] and
        center_face[1] > person_geometry[1] and
        center_face[1] < person_geometry[3]
    ):
        return True
    else:
        return False


def thread_change_video_address():
    while True:
        get_video_source_from_config_file()
        time.sleep(thread_sending_interval_video_address)


def thread_send_message_to_hub():
    global timestamps
    global timestamps_is_checked
    global ct
    while True:
        # Define send data format
        log.info("Value of persons are {}".format(ct.persons))
        data = {"timestamp": timestamps, "frames": [], "camID": mac_address}

        trackID_tmp = []

        for person in ct.persons.values():
            if person["is_sent"] is True:
                continue
            else:
                element_box = {
                    "trackID": None,
                    "timestamp": None,
                    "recognition": {},
                }
                element_box["trackID"] = person["trackID"]
                element_box["timestamp"] = person["timestamp"]
                element_box["recognition"] = person["recognition"]
                data["frames"].append(element_box)

                person["is_sent"] = True

                ct.update_persons(person["trackID"], person)
            if person["is_sent"] and person["is_exceed_threshold"]:
                trackID_tmp.append(person["trackID"])
        # Remove the trackID info that was sent to IoT Hub \
        # and exceed threshold
        for trackID in trackID_tmp:
            ct.deregister_persons(trackID)

        if data["frames"] is not None and len(data["frames"]) > 0:
            data["frames"] = sorted(data["frames"], key=lambda x: x["trackID"])
            timestamps_is_checked = False
            log.info("Just sent to Hub : {}".format(json.dumps(data)))
            iothub_client_run(json.dumps(data))
        else:
            log.info("No data for sending to IoT Hub")

        time.sleep(sending_interval)


# Running a thread for sending video address
thread_for_pub = threading.Thread(target=thread_change_video_address)
thread_for_pub.start()

# Running a thread for sending msg to hub
thread_for_send_msg = threading.Thread(target=thread_send_message_to_hub)
thread_for_send_msg.start()

base_box = {
    "trackID": 0,
    "timestamp": 1562241186.4627721,
    "recognition": {},
    "is_sent": False,
    "is_fulled": False,
    "is_exceed_threshold": False,
}

while True:
    log.info("Got a data from ncs2-manager!!!")
    json_data = sub.recv_json()
    person_rect = []
    # Extract frame data
    frame = json_data["frame"][0]
    timestamp = frame["timestamp"]

    if not len(frame["obj_boxes"]):
        log.info("Data with no person. Skip to next frame")
        # Update track ID
        objects = ct.update(person_rect)
        continue

    people = [
        x for x in frame["obj_boxes"] if x["detection"]["label"] == "person"
    ]
    faces = [
        x for x in frame["obj_boxes"] if x["detection"]["label"] == "face"
    ]

    for person in people:
        ymin, xmin, ymax, xmax = person["detection"]["box_geometry"]
        person_rect.append((xmin, ymin, xmax, ymax))

    # Update track ID
    objects = ct.update(person_rect)

    for person in people:
        ymin, xmin, ymax, xmax = person["detection"]["box_geometry"]
        cX = int((xmin + xmax) / 2.0)
        cY = int((ymin + ymax) / 2.0)

        # Create result object
        result_object = copy.deepcopy(base_box)
        result_object["timestamp"] = timestamp

        for face in faces:
            ymin_face, xmin_face, ymax_face, xmax_face = face["detection"][
                "box_geometry"
            ]
            if (
                check_point_in_polygon(
                    (ymin_face, xmin_face, ymax_face, xmax_face),
                    (ymin, xmin, ymax, xmax),
                ) and face["recognition"]
            ):
                result_object["recognition"] = {
                    "age_gender": face["recognition"]["age_gender"]
                }
                break
            else:
                log.info("Do not mapping face & person !!!")

        for (objectID, centroid) in objects.items():
            if (cX, cY) == (centroid[0], centroid[1]):
                result_object["trackID"] = objectID

                if objectID not in ct.persons:
                    if not timestamps_is_checked:
                        timestamps = timestamp

                    if result_object["recognition"]:
                        result_object["is_fulled"] = True
                    ct.update_persons(objectID, result_object)

                else:
                    current_tracker = ct.persons[objectID]

                    if (
                        current_tracker["is_fulled"] is not True and
                        result_object["recognition"]
                    ):
                        result_object["is_fulled"] = True
                        result_object["is_sent"] = False
                        log.info(
                            "Just update the track ID \
                            information: {}".format(
                                result_object
                            )
                        )
                        timestamps = timestamp
                        timestamps_is_checked = True
                        ct.update_persons(objectID, result_object)
