import util
import time
from enum import Enum
from ultralytics.engine.results import Results  # type: ignore
import socket
import json
import os

class ObjClasses(Enum):
    MANNEQUIN = 0
    TENT = 1

x_offset: list[float] = []
y_offset: list[float] = []
object_class: list[str] = []
latency_list: list[float] = []

# Telemetry transport configuration (default: send UDP packets to localhost:5600)
TELEMETRY_HOST = os.getenv("TELEMETRY_HOST", "127.0.0.1")
TELEMETRY_PORT = int(os.getenv("TELEMETRY_PORT", "5600"))

# UDP socket used to send telemetry payloads
telemetry_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def empty_lists() -> None:
    x_offset.clear()
    y_offset.clear()
    object_class.clear()
    latency_list.clear()

def add_results(results: list[Results], start_time: float) -> None:
    empty_lists()

    # Add new values to arrays
    for result in results:
        box = result.boxes
        if not box:
            continue
        x_offset.append(util.get_x_offset_deg(box))
        y_offset.append(util.get_y_offset_deg(box))
        object_class.append(result.names[box.cls.cpu().numpy()[0]])
        latency_list.append(time.time() - start_time)
    
    # Send telemetry payload (UDP JSON). If your robot expects MAVLink/mavsdk,
    # replace this function with the appropriate mavlink send logic.
    send_telemetry_data(x_offset, y_offset, object_class, latency_list)


def send_telemetry_data(x_off: list[float], y_off: list[float], obj_cls: list[str], lat: list[float]) -> None:
    """Serialize telemetry and send it to the main robot computer over UDP.

    This is a simple, dependency-free transport suitable for testing and for
    robots that accept JSON over UDP. If you want mavsdk/MAVLink, replace the
    body with mavsdk or pymavlink code that constructs the appropriate packet.
    """
    data = {
        "x_offset": x_off,
        "y_offset": y_off,
        "object_class": obj_cls,
        "latency": lat,
        "timestamp": time.time(),
    }
    try:
        telemetry_sock.sendto(json.dumps(data).encode("utf-8"), (TELEMETRY_HOST, TELEMETRY_PORT))
    except Exception as e:
        # Keep telemetry sending non-fatal; log the error to stdout/stderr
        print(f"Failed to send telemetry to {TELEMETRY_HOST}:{TELEMETRY_PORT}: {e}")
