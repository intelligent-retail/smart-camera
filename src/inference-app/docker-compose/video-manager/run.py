import os
import sys
import cv2
import json
import time
import base64
import datetime
import operator
import threading
import zmqutils
import logging as log
import platform
from shutil import rmtree


log.basicConfig(stream=sys.stdout, level=log.DEBUG)

video_src = os.getenv("VIDEO_SRC", 0)
buffer_less = os.getenv("BUFFER_LESS", True)
writer_interval = os.getenv("FRAME_INTERVAL", 5)
zmq_address_rep = os.getenv("ZMQ_VIDEO_ADDRESS_REP", "tcp://*:5562")
thread_reply_video_frame = int(
    os.getenv("THREAD_REPLY_VIDEO_FRAME", "90")
)

rep, ctx_rep = zmqutils.rep(zmq_address_rep)

log.info("Video Server is starting up...")


def is_rtsp_url(video_src):
    try:
        return video_src[:4] == "rtsp"
    except BaseException:
        return False


def is_pi_camera(video_src):
    return video_src == 0


def get_creation_date(path_to_file):
    if platform.system() == "Windows":
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            return stat.st_mtime


def send_message(file_name: str, timestamp, frame):
    if file_name == 0:
        file_name = "PI Camera"

    _, buffer = cv2.imencode(".jpg", frame)
    jpg_as_txt = base64.b64encode(buffer)

    message = json.dumps(
        {
            "file_name": file_name,
            "timestamp": timestamp,
            "frame": jpg_as_txt.decode("ascii"),
        }
    )
    rep.send_string(message)
    log.info("Just reply a frame to ncs2-manager !!!")


def stream_video_capture(src: str):
    # Open video source
    cap = cv2.VideoCapture(src, cv2.CAP_FFMPEG)
    while cap.grab():
        message_req = rep.recv_string()
        log.info("Data received content :{}".format(message_req))
        _, frame = cap.retrieve()
        send_message(src, frame)
    cap.release()


def video_capture(src: str, remove=False):
    # Open video source
    cap = cv2.VideoCapture(src, cv2.CAP_FFMPEG)
    real_fps = cap.get(cv2.CAP_PROP_FPS)
    log.info("video_capture ::: real fps: {}".format(real_fps))
    create_date = get_creation_date(src)

    log.info("This file was created at : {}".format(create_date))

    while True:
        try:
            message_req = rep.recv_string()
            log.info("Data received content :{}".format(message_req))
            ret, frame = cap.read()

            timestamps = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000

            log.info(
                "TS of this frame : {}, timestampe of this file : {} ".format(
                    timestamps, create_date + timestamps
                )
            )

            if not ret:
                message = json.dumps(
                    {"file_name": None, "timestamp": None, "frame": None}
                )
                rep.send_string(message)

                log.info("Just sent a frame to ncs2-manager")
                break
            else:
                timestamps += create_date

            send_message(src, timestamps, frame)
        except Exception as ex:
            log.error("Buffer less VideoCapture exception: {}".format(ex))

    cap.release()
    if remove:
        log.info("This file will be removed !!!! {}".format(src))
        os.remove(src)
        log.info("This file was removed !!!! {}".format(src))


def process_file(file_path, remove=False):
    if remove:
        log.info(
            "This file {} will be removed after finish reading".format(
                file_path
            )
        )
    else:
        log.info(
            "This file {} will be remain after finish reading".format(
                file_path
            )
        )

    _, ext = os.path.splitext(file_path)
    if ext in [".mp4", ".avi", ".mkv"]:
        try:
            video_capture(file_path, remove=remove)
        except Exception as ex:
            log.error("File {} read failed!".format(file_path))
            log.error("process_file ::: Exception: {}".format(ex))


def mkdir(dir_name: str, truncat=False):
    try:
        # Create target Directory
        os.mkdir(dir_name)
        log.info("Directory {} Created ".format(dir_name))

    except FileExistsError:
        if truncat:
            rmtree(dir_name, ignore_errors=True)

        log.warning("Directory {} already exists".format(dir_name))


def remove_tmpfile(src: str):
    files_list = os.listdir(src)
    for ftmp in files_list:
        if "_tmp" in ftmp:
            file_path = "{}/{}".format(src, ftmp)
            os.remove(file_path)
            log.info("Just removed tmp file : {}".format(file_path))


class VideoWriter(threading.Thread):
    def __init__(
        self,
        video_src=0,
        video_out_dir="./video_out/",
        usb_mode=False,
        resolution: tuple = (640, 480),
        capture_duration: int = 60,
    ):
        threading.Thread.__init__(self, daemon=True)

        self._video_src = video_src
        self._video_out_dir = os.path.abspath(video_out_dir)
        self._usb_mode = usb_mode
        self._resolution = resolution
        self._capture_duration = capture_duration

        try:
            if self._usb_mode:
                self.camera = cv2.VideoCapture(int(self._video_src))
            else:
                self.camera = cv2.VideoCapture(self._video_src, cv2.CAP_FFMPEG)

            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self._resolution[0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self._resolution[1])

            self.real_fps = self.camera.get(cv2.CAP_PROP_FPS)
            log.info("VideoWriter ::: real fps: {}".format(self.real_fps))

            self._capture_width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            self._capture_height = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            self._capture_fps = self.camera.get(cv2.CAP_PROP_FPS)
        except Exception as ex:
            log.error("Exception ::: {}".format(ex))

    def write_1_minute_video(self):

        log.info("Writing 1-minute video...")

        current_datetime = str(datetime.datetime.now())
        current_datetime = current_datetime.replace(" ", "_")
        current_datetime = current_datetime.replace(":", "-")

        output_file_name = "{}_tmp.mp4".format(current_datetime)
        final_file_name = "{}.mp4".format(current_datetime)
        output_file_name = os.path.join(self._video_out_dir, output_file_name)
        final_file_name = os.path.join(self._video_out_dir, final_file_name)
        # Define the codec and create VideoWriter object
        out = cv2.VideoWriter(
            output_file_name, 0x00000021, 15.0, self._resolution, True
        )
        log.info("File name: {}".format(output_file_name))
        start_time = time.time()
        log.info("Start at {}".format(start_time))

        counter = 1
        while int(time.time() - start_time) < self._capture_duration:
            try:
                ret, frame = self.camera.read()
                if (int(writer_interval) > 1) and (
                    not ret or counter % int(writer_interval) != 0
                ):
                    log.info("Skip this frame : {}".format(counter))
                    counter += 1
                    continue
                counter += 1
                # RTSP stream cannot be written into file
                # with given self._resolution
                if self._usb_mode:
                    frame = cv2.resize(frame, self._resolution)
                out.write(frame)
            except Exception as ex:
                log.error("VideoWriter ::: Exception: {}".format(ex))
        log.info("End at {}".format(time.time()))
        out.release()
        os.rename(output_file_name, final_file_name)
        log.info("Changed file name to mp4 format: {}".format(final_file_name))

    def run(self):
        # remove all tmp files in current folder except writing file
        remove_tmpfile(self._video_out_dir)
        while True:
            try:
                self.write_1_minute_video()
            except Exception as ex:
                log.error("VideoWriter ::: Exception: {}".format(ex))
                break

        self.camera.release()


# Video Writer
###############################################################################
video_out_dir = "./video_out"
video_mode = "rtsp"
video_src = str(video_src)

mkdir(video_out_dir)

if str.isdigit(video_src):
    video_mode = "usb"
    video_src = int(video_src)
else:
    if video_src[:10] == "/dev/video":
        video_mode = "usb"
        video_src = int(video_src[10:])
    elif is_rtsp_url(video_src):
        video_mode = "rtsp"
    else:
        video_mode = "file"

log.info("video_src: {}".format(video_src))
log.info("video_mode: {}".format(video_mode))

if video_mode == "usb":
    video_writer_thread = VideoWriter(
        video_src=video_src,
        video_out_dir=video_out_dir,
        usb_mode=True,
        resolution=(640, 480),
        capture_duration=60,
    )
    video_writer_thread.start()

if video_mode == "rtsp":
    video_writer_thread = VideoWriter(
        video_src=video_src,
        video_out_dir=video_out_dir,
        usb_mode=False,
        resolution=(640, 480),
        capture_duration=60,
    )
    video_writer_thread.start()

if video_mode not in ["usb", "rtsp"]:
    # remove all tmp files in current folder
    remove_tmpfile(os.path.abspath(video_src))
    video_out_dir = video_src
else:
    log.info("Wait for some seconds to prepare files in {}".format(video_mode))
    time.sleep(thread_reply_video_frame)

video_out_dir = os.path.abspath(video_out_dir)

while True:
    files_list = os.listdir(video_out_dir)
    fileData = {}
    for fname in files_list:
        if "_tmp" not in fname:
            file_path = "{}/{}".format(video_out_dir, fname)
            fileData[fname] = os.stat(file_path).st_mtime
    sortedFiles = sorted(fileData.items(), key=operator.itemgetter(1))

    if len(sortedFiles):
        try:
            oldest_file, timestamp = sortedFiles[0]
            if oldest_file:
                oldest_file = os.path.join(video_out_dir, oldest_file)

                log.info("READER ::: Oldest file: {}".format(oldest_file))
                if os.path.isfile(oldest_file):
                    process_file(oldest_file, remove=True)

        except Exception as ex:
            log.error(ex)

if video_mode in ["usb", "rtsp"]:
    video_writer_thread.join()

print("Done!")
