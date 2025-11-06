import os
import time
from typing import Optional, List, Tuple

import util
from ultralytics.engine.results import Results  # type: ignore
from pymavlink import mavutil

# MAVLink target (UDP out). Default commonly used port is 14550.
MAVLINK_TARGET_HOST = os.getenv("MAVLINK_TARGET_HOST", "127.0.0.1")
MAVLINK_TARGET_PORT = int(os.getenv("MAVLINK_TARGET_PORT", "14550"))

# mavlink_connection: initialized lazily when first send is attempted
_mavlink_conn: Optional[object] = None


def ensure_mavlink() -> Optional[object]:
    """Lazily create and return a pymavlink connection, or None on failure."""
    global _mavlink_conn
    if _mavlink_conn is not None:
        return _mavlink_conn
    try:
        uri = f"udpout:{MAVLINK_TARGET_HOST}:{MAVLINK_TARGET_PORT}"
        _mavlink_conn = mavutil.mavlink_connection(uri)
        return _mavlink_conn
    except Exception as e:
        print(f"Failed to open MAVLink connection to {MAVLINK_TARGET_HOST}:{MAVLINK_TARGET_PORT}: {e}")
        _mavlink_conn = None
        return None


def add_results(results: List[Results], start_time: float) -> None:
    """Select best detection for each class (0 and 1) and send scalar telemetry.

    For each class id in {0,1} we pick the detection with highest confidence
    across the provided Results. For each best detection we compute x/y
    offsets and latency then call send_telemetry_data(x, y, class_id, lat).
    """
    NUM_CLASSES = 2
    best_conf: List[float] = [-1.0] * NUM_CLASSES
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
    for info in best_info:
        if info is None:
            continue
        boxes, idx, cls_id = info
        try:
            box = boxes[idx]
        except Exception:
            box = boxes

        x = util.get_x_offset_deg(box)
        y = util.get_y_offset_deg(box)
        latency = time.time() - start_time

        send_telemetry_data(x, y, cls_id, latency)

def name_bytes(s: str) -> bytes:
    b = s.encode("ascii", "ignore")[:10]
    return b + b"\0" * (10 - len(b))

def send_telemetry_data(x: float, y: float, obj_cls: int, lat: float) -> None:
    """Send x, y and latency as three separate MAVLink messages.

    Uses the standard `named_value_float` MAVLink message .
    Each field is sent in its own message with a short
    name: 'vis_x', 'vis_y', 'vis_lat'.
    """
    conn = ensure_mavlink()
    if conn is None:
        # Connection unavailable — nothing to send.
        return

    # time_boot_ms: milliseconds since epoch (wrap to 32-bit)
    time_boot_ms = int(time.time() * 1000) & 0xFFFFFFFF

    try:
        conn.mav.named_value_float_send(time_boot_ms, name_bytes(f"vis_x{obj_cls}"), float(x))
        conn.mav.named_value_float_send(time_boot_ms, name_bytes(f"vis_y{obj_cls}"), float(y))
        conn.mav.named_value_float_send(time_boot_ms, name_bytes(f"vis_lat{obj_cls}"), float(lat))
    except Exception as e:
        print(f"Failed to send telemetry via named_value_float: {e}")
        return
