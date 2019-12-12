import os
import threading
import time
import queue as Queue
import cv2


class VideoCapture:
    """Buffer less VideoCapture"""

    def __init__(self, video_src, bless=True):
        """Buffer less Video Capture
            Args:
                video_src: str
                bless: True
            Return
        """
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"

        self.bless = bless

        # Open video source
        self.cap = cv2.VideoCapture(video_src, cv2.CAP_FFMPEG)
        self.video_width = self.cap.get(3)
        self.video_height = self.cap.get(4)

        # Internal buffer will now store only 3 frames
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)

        # Check if camera opened successfully
        if not self.cap.isOpened():
            print("Error opening video stream or file")
            exit(1)

        self.q = Queue.Queue()

        t = threading.Thread(target=self._reader, name="Video Processor")
        t.daemon = True
        t.start()

    def _reader(self):
        """Read frames as soon as they are available, keeping only most recent one"""
        while self.cap.grab():
            # # Capture frame-by-frame
            # if not self.cap.grab():
            #     time.sleep(1)
            #     continue
            if not self.q.empty() and self.bless:
                try:
                    self.q.get_nowait()  # discard previous (unprocessed) frame
                except Queue.Empty:
                    pass
            _, frame = self.cap.retrieve()
            self.q.put(frame)

    def read(self):
        """Get 1 frame"""
        return self.q.get()

    def get_width(self):
        return self.video_width

    def get_height(self):
        return self.video_height
