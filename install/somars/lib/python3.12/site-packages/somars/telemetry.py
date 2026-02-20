import os
import time
from typing import Optional, List, Tuple

from ultralytics.engine.results import Results  # type: ignore
import rclpy
from rclpy.node import Node

from somars import util
from messages.msg import Detection  # type: ignore
from std_msgs.msg import String

# Minimum confidence threshold for object detection
MIN_CONFIDENCE = 0.5

def add_results(results: List[Results], start_time: float, node) -> None:
    """Select best detection for each class (0 and 1) and send scalar telemetry.

    For each class id in {0,1} we pick the detection with highest confidence
    across the provided Results. For each best detection we compute x/y
    offsets and latency then call send_telemetry_data(x, y, class_id, lat).
    """
    NUM_CLASSES = 2
    best_conf: List[float] = [MIN_CONFIDENCE] * NUM_CLASSES
    best_info: List[Optional[Tuple[object, int, int]]] = [None] * NUM_CLASSES

    for result in results:
        boxes = result.boxes
        if not boxes:
            continue
        # Try to read confidence and class arrays from the Boxes object.
        try:
            confs = boxes.conf.cpu().numpy()
            clss = boxes.cls.cpu().numpy().astype(int)
        except Exception:
            # If the Boxes API is different, skip this result.
            continue

        for i, conf in enumerate(confs):
            cls_id = int(clss[i])
            if 0 <= cls_id < NUM_CLASSES and float(conf) > best_conf[cls_id]:
                best_conf[cls_id] = float(conf)
                best_info[cls_id] = (boxes, int(i), cls_id)

    # Send telemetry for each class if we found a detection
    for i in range(len(best_info)):
        info = best_info[i]
        if info is None:
            send_telemetry_data(0, 0, i, 0, False, node)
            continue
        boxes, idx, cls_id = info
        try:
            box = boxes[idx]
        except Exception:
            box = boxes

        x = util.get_x_offset_deg(box)
        y = util.get_y_offset_deg(box)
        latency = time.time() - start_time

        send_telemetry_data(x, y, cls_id, latency, True, node)

signal = ''

def setSignal(msg):
    global signal
    if signal == 'generate':
        return
    if signal == 'picture' and msg.data != 'generate':
        return
    signal = msg.data

def init(node):
    node.resultPublisher = node.create_publisher(Detection, 'detection', 10)
    node.mappingSubscriber = node.create_subscription(String, 'mapping', setSignal, 10)

def send_telemetry_data(x: float, y: float, obj_cls: int, lat: float, detected: bool, node) -> None:
    """Send x, y and latency as a single ROS message.
    """
    msg = Detection()
    msg.x = x
    msg.y = y
    msg.class_id = obj_cls
    msg.latency = lat
    node.resultPublisher.publish(msg)

def get_signal():
    """Get an input signal from the FCU as a string"""
    global signal
    s = signal
    signal = ''
    return s