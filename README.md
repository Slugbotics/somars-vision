# somars-vision

Repository for running the object detection model and mapping code for the 2026 SUAS competition.

---

## File Descriptions

### `main.py`
The primary production entry point for the vision system. On startup it loads a YOLOv8 mannequin detection model (`models/mannequinmodel.pt`) and opens up to 5 camera feeds concurrently, each in its own thread. Each frame is passed through the YOLO tracker, and the annotated result is overlaid with a crosshair HUD and FPS counter. Annotated frames are streamed via MJPEG on port 5090 and displayed in live OpenCV windows. Detection results (x/y angular offsets, latency, and a detection flag) are forwarded to a flight controller over MAVLink UDP. A separate image-storage thread listens for MAVLink `STATUSTEXT` signals from the FCU: a `"picture"` signal saves the current frame to the `images/` folder, and a `"generate"` signal triggers orthophoto map generation via `mapping.py`. The NodeODM mapping backend is initialized in the background on startup. Graceful shutdown is handled on `Ctrl+C` / `SIGTERM`.

### `test_main.py`
A standalone testing variant of `main.py` intended for use without a connected flight controller. It is structurally identical to `main.py` except that image capture is driven by a timer rather than MAVLink signals — it automatically saves one frame per second until `NUM_IMAGES` (50) images have been collected, then triggers map generation. Telemetry sending is omitted. This allows the full detection-and-mapping pipeline to be validated offline.

### `mapping.py`
Handles aerial orthophoto map generation using OpenDroneMap (ODM). It first ensures a NodeODM Docker container is running locally (pulling and starting the `opendronemap/nodeodm` image if needed, then waiting up to 10 minutes for the HTTP endpoint to become available). Once connected, `generate_map()` submits all images from the `images/` folder to NodeODM as a processing task with fast-orthophoto settings, waits for completion, downloads the resulting GeoTIFF, converts it to a PNG named `UCSC_SOMARS_map.png`, and then polls until a USB drive is detected and copies the map to it.

### `telemetry.py`
Manages all MAVLink communication with the flight controller. It exposes two lazily-initialized connections: an outbound UDP connection that sends detection data as `named_value_float` / `named_value_int` MAVLink messages (fields `vis_x`, `vis_y`, `vis_lat`, `vis_det` per class), and an inbound UDP listener that reads `STATUSTEXT` messages from the FCU. `add_results()` selects the highest-confidence detection per class from a YOLO results list, computes angular offsets via `util.py`, and dispatches the telemetry. `get_signal()` drains pending `STATUSTEXT` messages and returns the highest-priority command string (`"generate"` > `"picture"`).

### `util.py`
Provides helper functions for converting YOLO bounding box positions into angular offsets relative to the camera's optical center. `get_x_offset_deg()` and `get_y_offset_deg()` each normalise the bounding box center coordinate against the frame dimensions, project it through the camera's field of view (configured for an Arducam at 70° H × 43.75° V), and return the offset in degrees. These values are used by `telemetry.py` to report where a detected target is pointing relative to the drone's camera.
