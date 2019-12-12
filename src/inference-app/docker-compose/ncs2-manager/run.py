from __future__ import print_function
import os
import sys
import cv2
import json
import time
import base64
import datetime
import numpy as np
import logging as log
import threading
import zmqutils


try:
    from openvino.inference_engine import IENetwork, IEPlugin
except BaseException:
    from armv7l.openvino.inference_engine import IENetwork, IEPlugin


log.basicConfig(stream=sys.stdout, level=log.DEBUG)

show_gui = os.getenv("SHOW_GUI", "False") == "True"
initial_w = int(os.getenv("INITIAL_W", 640))
initial_h = int(os.getenv("INITIAL_H", 480))
zmq_address_pub = os.getenv("ZMQ_ADDRESS_PUB", "tcp://*:5560")
zmq_video_address_sub = os.getenv(
    "ZMQ_VIDEO_ADDRESS_SUB", "tcp://inference-engine:5561"
)
person_detection_threshold = os.getenv("PERSON_DETECTION_THRESHOLD", "0.8")
face_detection_threshold = os.getenv("FACE_DETECTION_THRESHOLD", "0.8")
thread_got_interval_video_address = int(
    os.getenv("THREAD_GET_INTERVAL_VIDEO_ADDRESS", "20")
)

check_flag = False
zmq_video_req = ""
pub, pub_ctx = zmqutils.pub(zmq_address_pub)
sub_video_address, sub_video_address_ctx = zmqutils.sub(zmq_video_address_sub)
video_address_new = ""


def get_frame():
    global video_address_new
    chk_flag = False
    SOURCE = None
    file_name = None

    if video_address_new != "":
        req, _ = zmqutils.req(video_address_new)

        if req is None:
            log.info("This video source is not correct!!!")
            return None, None, None

        log.info("Video_address is: {}".format(video_address_new))
        chk_flag = True

    if chk_flag:
        log.info("Request get a frame ...")
        req.send_string("Request get a frame ...")
        log.info("Sent a request to video-manager")

        raw_message = req.recv_string()  # string
        log.info("Got a frame result from video-manager")
        message = json.loads(raw_message)  # dict

        file_name = message["file_name"]
        timestamp = message["timestamp"]
        if message["frame"] is not None:
            FRAME = base64.b64decode(message["frame"])
            NP_IMGAGE = np.fromstring(FRAME, dtype=np.uint8)
            SOURCE = cv2.imdecode(NP_IMGAGE, 1)

        return SOURCE, file_name, timestamp
    else:
        # log.info("No data in get frame")
        return None, None, None


def get_agegender(face_img, exec_net, c, h, w):
    GENDER = ["FEMALE", "MALE"]
    # Resize image

    processedImg = cv2.resize(face_img, (h, w))

    # Change data layout from HWC to CHW
    processedImg = processedImg.transpose((2, 0, 1))
    processedImg = processedImg.reshape((1, c, h, w))

    ag_res = exec_net.infer(inputs={input_blob_agegender: processedImg})
    # Handling age
    age = ag_res["age_conv3"]
    age = int(age * 100)

    # Handling gender
    probs = ag_res["prob"]
    max_prob_idx = np.argmax(probs)
    gender = GENDER[max_prob_idx]

    return age, gender, float(np.amax(probs))


def get_agegender_async(request_id):
    GENDER = ["FEMALE", "MALE"]

    # Parse detection results of the current request
    ag_res = exec_net_agegender.requests[request_id].outputs[
        out_blob_agegender
    ]

    # Handling age
    age = ag_res["age_conv3"]
    age = int(age * 100)

    # Handling gender
    gender = ag_res["prob"]
    gender = np.argmax(gender)
    gender = GENDER[gender]

    return age, gender


def get_exec_net(model_name, model_xml, model_bin, is_multi_keys=True):
    """Get exec_net
                Args:
                        model_name, model_xml, model_bin, is_multi_keys=False
                Returns:
                        exec_net, input_blob, out_blob, (n, c, h, w)
        """

    log.info("Reading IR for {}...".format(model_name))
    net = IENetwork(model=model_xml, weights=model_bin)

    if is_multi_keys:
        assert (
            len(net.inputs.keys()) == 1
        ), "Demo supports only single input topologies"

        assert (
            len(net.outputs) == 1
        ), "Demo supports only single output topologies"

    input_blob = next(iter(net.inputs))
    out_blob = next(iter(net.outputs))

    log.info("Loading model {} to the plugin".format(model_name))
    exec_net = plugin.load(network=net, num_requests=num_requests)

    # Read and pre-process input image
    n, c, h, w = net.inputs[input_blob].shape
    del net

    return exec_net, input_blob, out_blob, (n, c, h, w)


num_requests = 2

# Plugin initialization for specified device
# and load extensions library if specified
# -------------------- 1. Load Plugin for inference engine --------------------
DEVICE = "MYRIAD"

log.info("Initializing plugin for {} device...".format(DEVICE))
plugin = IEPlugin(device=DEVICE, plugin_dirs=None)

log.info("Loading network files")

exec_net, input_blob, out_blob, (n, c, h, w) = get_exec_net(
    "Person Detection",
    "FP16/person-detection-retail-0013-fp16.xml",
    "FP16/person-detection-retail-0013-fp16.bin",
)

exec_net_face, input_blob_face, out_blob_face, (n2, c2, h2, w2) = get_exec_net(
    "Face Detection",
    "FP16/face-detection-adas-0001.xml",
    "FP16/face-detection-adas-0001.bin",
)

exec_net_agegender, input_blob_agegender, out_blob_agegender, (
    n3,
    c3,
    h3,
    w3,
) = get_exec_net(
    "Age Gender Classification",
    "FP16/age-gender-recognition-retail-0013-fp16.xml",
    "FP16/age-gender-recognition-retail-0013-fp16.bin",
    is_multi_keys=False,
)

cur_request_id = 0
next_request_id = 1

person_rect = []
faces = []


def thread_get_video_address():
    global video_address_new
    while True:
        log.info("Thread to get video address")
        try:
            video_source_address = sub_video_address.recv_string()
            json_vs = json.loads(video_source_address)

            video_address_new = json_vs["video_address"]
        except Exception as ex:
            log.error("thread_get_video_address exception: {}".format(ex))
        time.sleep(thread_got_interval_video_address)


log.info("Running a thread for get video address")
thread_for_pub = threading.Thread(target=thread_get_video_address)
thread_for_pub.start()

frame, file_name, timestamp = get_frame()

age, gender = None, None
objects = None
total_time = 0
agv_fps = None


def generate_json_result():
    boxes = {"obj_boxes": [], "timestamp": None}

    data = {"frame": []}

    return data, boxes


print(
    "To close the application, press any key \
with focus on the output window, TAB to change async mode"
)

while True:
    data, boxes = generate_json_result()

    frame, file_name, timestamp = get_frame()

    if file_name is None or file_name == "":
        # Send JSON data to inference engine
        data["frame"].append(boxes)
        pub.send_json(data, flags=0)
        log.info("Just sent a data to inference-engine. {}".format(data))
        continue

    inf_start = time.time()
    inf_end = None
    det_time = None

    boxes["timestamp"] = timestamp

    # Person detection
    person_in_frame = cv2.resize(frame, (w, h))
    person_in_frame = person_in_frame.transpose(
        (2, 0, 1)
    )  # Change data layout from HWC to CHW
    person_in_frame = person_in_frame.reshape((n, c, h, w))
    exec_net.start_async(
        request_id=cur_request_id, inputs={input_blob: person_in_frame}
    )

    person_rect = []
    # Person detection
    if exec_net.requests[cur_request_id].wait(-1) == 0:

        # Parse detection results of the current request
        res = exec_net.requests[cur_request_id].outputs[out_blob]
        for obj in res[0][0]:
            # Draw only objects
            # when probability more than specified threshold
            if obj[2] > float(person_detection_threshold):
                xmin = max(0, int(obj[3] * initial_w))
                ymin = max(0, int(obj[4] * initial_h))
                xmax = max(0, int(obj[5] * initial_w))
                ymax = max(0, int(obj[6] * initial_h))
                # JSON OUT
                box = {
                    "detection": {
                        "box_geometry": [xmin, ymin, xmax, ymax],
                        "label": "person",
                    },
                    "recognition": {},
                }
                boxes["obj_boxes"].append(box)

                person_rect.append((xmin, ymin, xmax, ymax, obj[2]))

                text = "person: " + str(round(obj[2] * 100, 1)) + " %"

                if show_gui:
                    color = (0, 0, 0)
                    cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
                    cv2.putText(
                        frame,
                        text,
                        (xmin, ymin - 7),
                        cv2.FONT_HERSHEY_COMPLEX,
                        0.6,
                        color,
                        1,
                    )
    if len(person_rect) > 0:
        log.info("Starting face detection")
        # Face detection
        face_in_frame = cv2.resize(frame, (w2, h2))
        face_in_frame = face_in_frame.transpose(
            (2, 0, 1)
        )  # Change data layout from HWC to CHW
        face_in_frame = face_in_frame.reshape((n, c2, h2, w2))

        exec_net_face.start_async(
            request_id=cur_request_id, inputs={input_blob_face: face_in_frame}
        )

        if exec_net_face.requests[cur_request_id].wait(-1) == 0:
            # Parse detection results of the current request
            res = exec_net_face.requests[cur_request_id].outputs[out_blob_face]

            faces = []

            for obj in res[0][0]:
                # Draw only objects
                # when probability more than specified threshold
                if obj[2] > float(face_detection_threshold):
                    xmin = max(0, int(obj[3] * initial_w))
                    ymin = max(0, int(obj[4] * initial_h))
                    xmax = max(0, int(obj[5] * initial_w))
                    ymax = max(0, int(obj[6] * initial_h))

                    face_croped = frame[ymin:ymax, xmin:xmax]

                    faces.append(
                        (
                            face_croped,
                            obj[2],
                            {"age": None, "gender": None},
                            (xmin, ymin, xmax, ymax),
                        )
                    )

            recognized_faces = []
            for face, prob, ag, (xmin, ymin, xmax, ymax) in faces:
                age, gender = None, None

                # JSON OUT
                box = {
                    "detection": {
                        "box_geometry": [xmin, ymin, xmax, ymax],
                        "label": "face",
                    },
                    "recognition": {},
                }

                try:
                    age, gender, ag_prob = get_agegender(
                        face, exec_net_agegender, c3, h3, w3
                    )
                    recognized_faces.append(
                        (
                            face,
                            prob,
                            {
                                "age": age,
                                "gender": gender,
                                "confidence": float(ag_prob),
                            },
                            (xmin, ymin, xmax, ymax),
                        )
                    )
                    # JSON OUT
                    box["recognition"] = {
                        "age_gender": {"age": age, "gender": gender}
                    }

                    text = "face: {}% {} - {}".format(
                        round(prob * 100, 1), age, gender
                    )
                    if show_gui:
                        color = (0, 255, 0)
                        cv2.rectangle(
                            frame, (xmin, ymin), (xmax, ymax), color, -1
                        )
                        cv2.putText(
                            frame,
                            text,
                            (xmin, ymin - 7),
                            cv2.FONT_HERSHEY_COMPLEX,
                            0.6,
                            color,
                            1,
                        )
                except BaseException:
                    pass

                boxes["obj_boxes"].append(box)
            faces = recognized_faces

    inf_end = time.time()
    det_time = inf_end - inf_start
    total_time += datetime.timedelta(seconds=det_time).total_seconds()

    if show_gui:
        cv2.imshow("Detection Results", frame)

    fps_rate = 1 / datetime.timedelta(seconds=det_time).total_seconds()

    # Send JSON data to inference engine
    data["frame"].append(boxes)
    pub.send_json(data, flags=0)
    log.info("Just sent a data to inference-engine. {}".format(data))

    if show_gui:
        key = cv2.waitKey(1) & 0xFF

        if 27 == key:  # ESC
            break

if show_gui:
    # cap.release()
    cv2.destroyAllWindows()
