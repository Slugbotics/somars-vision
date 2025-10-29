# Original version copied from FRC team 972's 2024-Coprocessor-Vision repository

#! ./venv/bin/python3
from threading import Thread
import cv2
import numpy as np
from ultralytics import YOLO # type: ignore
from ultralytics.engine.results import Results # type: ignore
import time
import telemetry
import snapshotter
import signal
import sys
import platform
import functools
import subprocess
import os
from mjpeg_streamer import MjpegServer, Stream
from queue import Empty, Queue, Full
import util

# Model path
MODEL_PATH = "models/mannequinmodel.pt"

# Define camera indexes to display in separate windows
# Reverted to a fixed set to ensure all potential feeds create windows
cameras: list[int] = [i for i in range(5)]

# ANSI colors
COLOR_BOLD = "\033[1m"
COLOR_RESET = "\033[0m"

# are we running interactively?
is_interactive: bool = sys.stderr.isatty()

# disable when not needed to improve performance
enable_mjpeg: bool = is_interactive
# We support on-screen windows on all OSes by doing GUI work on the main thread.
enable_display: bool = True  # show OpenCV windows while detecting

# Opt-in: skip macOS AVFoundation auth prompt/loop handling
# Set via env SOMARS_SKIP_MACOS_AUTH=1 to enable skipping
SKIP_MACOS_AUTH: bool = bool(int(os.getenv("SOMARS_SKIP_MACOS_AUTH", "0")))
if platform.system() == "Darwin" and SKIP_MACOS_AUTH:
    os.environ["OPENCV_AVFOUNDATION_SKIP_AUTH"] = "1"

is_interrupted: bool = False

@functools.cache # only run once
def get_ips() -> list[str]:
    ip_list: list[str] = []
    if (platform.system() == "Linux"): # screw windows
       ipstr: str = subprocess.check_output(["hostname", "-I"]) \
           .decode("UTF-8").rstrip("\n").strip()
       ip_list = ipstr.split(" ")
    ip_list.append("localhost")
    return ip_list

def handle_signal(signalnum, stack_frame):
    # parameters are provided by the signal module but intentionally unused
    raise SystemExit()

# handle SIGTERM nicely
signal.signal(signal.SIGTERM, handle_signal)

# Load the model
model = YOLO(MODEL_PATH)

# exit gracefully on ^C
is_interrupted: bool = False
print("Program started")

def run_cam_in_thread(cameraname: int, q: Queue) -> None:
    video: cv2.VideoCapture = cv2.VideoCapture(cameraname)  # Read the video file

    while True:
        ret: bool
        frame: np.ndarray
        ret, frame = video.read()  # Read the video frames
        start_time: float = time.time()

        # exit if no frames remain
        if not ret:
            break
    
        if is_interrupted:
            break

        # Empty the queue if it is full so the frame in it is the most recent one
        if q.full():
            # This should almost never happen, but it avoids any potential errors if it is emptied between calling full and get
            try:
                q.get_nowait()
            except Empty:
                pass
        try:
            q.put_nowait((frame.copy(), start_time))
        except Full:
            pass

    print(f"CAMERA {cameraname} EXITING (camera thread)")
    # Release video sources
    video.release()
        


def run_tracker_in_thread(cameraname: int, stream: Stream, out_q: Queue) -> None:
    """
    Runs a video file or webcam stream concurrently with the YOLOv8 model using threading.

    This function captures video frames from a given file or camera source and utilizes the YOLOv8 model for object
    tracking. The function runs in its own thread for concurrent processing.

    Args:
        cameraname (int): The identifier for the webcam/external camera source.

    Note:
        Press 'q' to quit the video display window.
    """

    q: Queue = Queue(maxsize=1)
    cam_thread = Thread(target=run_cam_in_thread, args=(cameraname, q), daemon=False)
    cam_thread.start()

    snapshot_time: float = time.time()
    
    global is_interrupted

    print(f"Camera {cameraname} activating")

    # Exit the loop if no more frames in the video
    while not is_interrupted and cam_thread.is_alive():
        if (is_interactive):
            print(f"Camera: {cameraname}") # For debugging 


        try:
            start_time: float
            frame: np.ndarray
            frame, start_time = q.get(block=True, timeout=5)
        except Empty: # stop the thread getting stuck if the camera thread immidiately dies
            continue

        # Track objects in frames if available
        results: list[Results] = model.track(frame, persist=True, verbose=is_interactive)
        res_plotted: np.ndarray = results[0].plot()
        # Calculate offsets
        telemetry.add_results(results, start_time)
        end_time: float = time.time()

        if results[0] is not None and len(results[0].boxes) != 0 and len(results[0].boxes[0]) is not None:
            print("x: " + str(util.get_x_offset_deg(results[0].boxes)))
            print("y: " + str(util.get_y_offset_deg(results[0].boxes)))

        if (time.time() - snapshot_time > 10): # snapshot every x seconds
            snapshotter.submit(results[0])
            snapshot_time = time.time()

        # Overlay HUD and stream via MJPEG
        elapsed = end_time - start_time
        fps: float = round(1 / elapsed, 2) if elapsed > 1e-6 else 0.0
        center: tuple[int, int] = (res_plotted.shape[1] // 2, res_plotted.shape[0] // 2)
        size: int = 50
        cv2.line(res_plotted, (center[0] - size, center[1]), (center[0] + size, center[1]), (0, 128, 255), 5)
        cv2.line(res_plotted, (center[0], center[1] - size), (center[0], center[1] + size), (0, 128, 255), 5)
        cv2.putText(res_plotted, str(fps), (7, 70), cv2.FONT_HERSHEY_SIMPLEX, 3, (100, 255, 0), 3, cv2.LINE_AA)

        if enable_mjpeg and stream is not None:
            stream.set_frame(res_plotted)

        # Send frame to main-thread display queue
        if enable_display:
            if out_q.full():
                try:
                    out_q.get_nowait()
                except Empty:
                    pass
            try:
                out_q.put_nowait(res_plotted)
            except Full:
                pass

    cam_thread.join()
    print(f"CAMERA {cameraname} EXITING (detector thread)")


if (enable_mjpeg):
    stream: Stream = Stream("Detectorator", size=(640, 480), quality=50, fps=10)
    server: MjpegServer = MjpegServer("0.0.0.0", 5090)
    server.add_stream(stream)
    server.start()
else:
    stream = None

threads: list[Thread] = []

# On macOS, preflight camera permissions on the main thread so AVFoundation prompts can appear
if platform.system() == "Darwin" and not SKIP_MACOS_AUTH:
    for c in cameras:
        cap = cv2.VideoCapture(c)
        # A brief read attempt can help trigger permission; ignore failures
        try:
            _ = cap.read()
        except Exception:
            pass
        cap.release()

# Per-camera queues for main-thread display
display_queues: dict[int, Queue] = {c: Queue(maxsize=1) for c in cameras}

for c in cameras:
    # Create the thread
    # daemon=True makes it shut down if something goes wrong
    thread = Thread(target=run_tracker_in_thread, args=(c, stream, display_queues[c]), daemon=True)
    # Add to the array to use later
    threads.append(thread)
    # Start the thread
    thread.start()

snapshot_thread: Thread = Thread(target=snapshotter.run_snapshotter_thread, daemon=True)
snapshot_thread.start()

try:
    if enable_display:
        # Create windows on main thread
        for c in cameras:
            window_name = f"Camera {c}"
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, 960, 540)

        while True:
            # Show latest frames if available
            for c in cameras:
                window_name = f"Camera {c}"
                try:
                    frame = display_queues[c].get_nowait()
                except Empty:
                    frame = None
                if frame is not None:
                    cv2.imshow(window_name, frame)

            # Handle key events
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                print("Quit requested from window")
                is_interrupted = True
                break

            # Also break if all threads have exited
            if all(not t.is_alive() for t in threads):
                break

            time.sleep(0.001)
    else:
        while True:
            time.sleep(1)
except (KeyboardInterrupt, SystemExit) as e:
    print(COLOR_BOLD, "INTERRUPT RECIEVED -- EXITING", COLOR_RESET, sep="")
    is_interrupted = True

# Wait for the tracker threads to finish
for thread in threads:
    thread.join()

if (enable_mjpeg):
    # Clean up
    server.stop()
    
if enable_display:
    cv2.destroyAllWindows()