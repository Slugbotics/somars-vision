import http.client
import os
import socket
import subprocess
import time
import shutil
import getpass
import threading
from typing import Optional

from pyodm import Node

FILE_NAME = "UCSC_SOMARS_map.png"

node: Node = None
initialized: bool = False
lock: threading.Lock = threading.Lock()
stop_event: threading.Event = threading.Event()

def _run_cmd(cmd: list[str]) -> tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out, err = proc.communicate()
        return proc.returncode, out.strip(), err.strip()
    except Exception as e:
        return -1, "", str(e)


def ensure_nodeodm_container(name: str = "nodeodm", image: str = "opendronemap/nodeodm:latest", port: int = 3000) -> bool:
    """Ensure a Docker container running NodeODM is available locally.

    Returns True when the NodeODM HTTP endpoint is reachable on localhost:port.
    If Docker is not installed or the container cannot be started, returns False.
    """
    # Check docker exists
    rc, _, _ = _run_cmd(["docker", "--version"])
    if rc != 0:
        print("Docker CLI not found or not runnable. Install Docker or ensure 'docker' is on PATH.")
        return False

    # Check if container exists
    rc, out, _ = _run_cmd(["docker", "ps", "-a", "--filter", f"name={name}", "--format", "{{.Names}} {{.Status}}"])
    if rc != 0:
        print("Failed to list docker containers")
        return False

    if out:
        # If container exists, see if it's running
        if name in out and "Up" in out:
            print(f"Container '{name}' already running")
        else:
            # start container
            print(f"Starting existing container '{name}'...")
            rc, _, err = _run_cmd(["docker", "start", name])
            if rc != 0:
                print(f"Failed to start container {name}: {err}")
                return False
    else:
        # Pull image and run container
        print(f"Creating and starting container '{name}' from image {image}...")
        rc, _, err = _run_cmd(["docker", "pull", image])
        if rc != 0:
            print(f"Failed to pull image {image}: {err}")
            return False
        rc, _, err = _run_cmd([
            "docker",
            "run",
            "-d",
            "--restart",
            "unless-stopped",
            "-p",
            f"{port}:{port}",
            "--name",
            name,
            image,
        ])
        if rc != 0:
            print(f"Failed to run container {name}: {err}")
            return False

    # Wait for HTTP endpoint
    deadline = time.time() + 600.0
    while time.time() < deadline:
        try:
            conn = http.client.HTTPConnection("localhost", port, timeout=2)
            conn.request("GET", "/")
            resp = conn.getresponse()
            # any response means the server is up
            print("NodeODM responded")
            return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            time.sleep(1.0)
        except Exception as e:
            print(f"HTTP check error: {e}")
            time.sleep(1.0)

    print("Timed out waiting for NodeODM to become available on localhost:%d" % port)
    return False


def initialize():
    """Initialize the NodeODM connection, starting container if needed."""
    global node, initialized
    with lock:
        if node is not None:
            return
        if not ensure_nodeodm_container():
            print("NodeODM not available; aborting connection attempt")
            return
        try:
            node = Node("localhost", 3000)
            initialized = True
        except Exception as e:
            print(f"Failed to create Node: {e}")
    print("Connected to NodeODM at localhost:3000")


def _is_mount(path: str) -> bool:
    """Return True if the given path is a mount point."""
    try:
        return os.path.ismount(path)
    except Exception:
        return False


def _find_usb_mount() -> Optional[str]:
    """Try to locate a mounted USB drive and return its mount path or None."""
    # POSIX detection
    user = None
    try:
        user = getpass.getuser()
    except Exception:
        user = None

    candidates = []
    if user:
        candidates.extend([f"/run/media/{user}", f"/media/{user}"])
    candidates.extend(["/media", "/run/media", "/mnt"])

    for base in candidates:
        if os.path.isdir(base):
            # return the first non-empty subdirectory
            try:
                for sub in os.listdir(base):
                    path = os.path.join(base, sub)
                    if os.path.isdir(path) and _is_mount(path):
                        return path
            except Exception:
                continue

    # Fallback: parse /proc/mounts for typical removable devices
    try:
        if os.path.exists("/proc/mounts"):
            with open("/proc/mounts", "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2:
                        mount_point = parts[1]
                        fs = parts[2] if len(parts) > 2 else ""
                        if mount_point.startswith("/media") or mount_point.startswith("/run/media") or mount_point.startswith("/mnt"):
                            # heuristics: prefer vfat, exfat, ntfs, or device-based mounts
                            if fs.lower() in ("vfat", "exfat", "ntfs", "fuseblk") or parts[0].startswith("/dev/"):
                                if os.path.isdir(mount_point):
                                    return mount_point
    except Exception:
        pass

    return None


def copy_output_to_usb(output_folder: str) -> bool:
    """Copy the contents of `output_folder` to a detected USB mount.

    Returns True on success, False if no USB found or copy failed.
    """
    mount = _find_usb_mount()
    if not mount:
        return False

    # Ensure mount is writable
    if not os.access(mount, os.W_OK):
        return False

    src = os.path.join(output_folder, FILE_NAME)
    if not os.path.exists(src):
        return False

    dst = os.path.join(mount, FILE_NAME)
    # If destination exists, remove it to allow overwrite
    if os.path.exists(dst):
        try:
            if os.path.islink(dst) or os.path.isfile(dst):
                os.remove(dst)
            else:
                shutil.rmtree(dst)
        except Exception as e:
            return False

    try:
        shutil.copy2(src, dst)
        return True
    except Exception as e:
        return False

def generate_map():
    """Generates the map using images in the folder images and saves output to output folder."""
    global node, initialized
    if not initialized:
        initialize()
    with lock:
        if node is None:
            print("ODM node not initialized; cannot generate map")
            return

        image_folder = os.path.abspath("images")
        output_folder = os.path.abspath("output")

        if not os.path.isdir(image_folder):
            print("Could not find images folder")
            return

        image_paths: list[str] = []
        for name in os.listdir(image_folder):
            full = os.path.join(image_folder, name)
            if os.path.isfile(full):
                image_paths.append(full)

        if len(image_paths) == 0:
            print("No image files found")
            return

        os.makedirs(output_folder, exist_ok=True)

        try:
            # Create and run the processing task
            options = {
                "fast-orthophoto": True,
                "end-with": "odm_orthophoto",
                "skip-report": True,
                "skip-3dmodel": True,
                "orthophoto-png": True,
                "orthophoto-format": "png",
                # Tune this to change map quality. Low values = higher quality, 5 is the default
                "orthophoto-resolution": 5
            }
            # Request both PNG and TIFF orthophoto so we have a fallback
            outputs = [
                "odm_orthophoto/odm_orthophoto.png",
                "odm_orthophoto/odm_orthophoto.tif"
            ]
            task = node.create_task(image_paths, options=options, outputs=outputs, name=f"Mapping-{int(time.time())}")
            print("Task created, waiting for completion...")
            task.wait_for_completion()
            print("Task completed. Downloading results...")
            task.download_assets(output_folder)
            print("Results downloaded")
            
            # Copy the produced PNG into the top-level output folder using the desired name
            try:
                ortho_dir = os.path.join(output_folder, "odm_orthophoto")
                if os.path.isdir(ortho_dir):
                    src_png = os.path.join(ortho_dir, "odm_orthophoto.png")
                    if os.path.exists(src_png):
                        dst_png = os.path.join(output_folder, FILE_NAME)
                        try:
                            shutil.copy2(src_png, dst_png)
                            print(f"Saved orthophoto as {dst_png}")
                        except Exception as e:
                            print(f"Failed to save orthophoto {src_png} -> {dst_png}: {e}")
            except Exception as e:
                print(f"Orthophoto rename step failed: {e}")

            # Copy map to USB drive (wait until a USB is mounted)
            while not copy_output_to_usb(output_folder):
                # If main thread signalled stop, abort waiting
                if stop_event.is_set():
                    return
                print("Waiting for USB drive to be mounted... (press Ctrl-C to abort)")
                time.sleep(2)
            print("Output copied to USB drive.")

        except Exception as e:
            print(f"Failed to create or process ODM task: {e}")

if __name__ == "__main__":
    generate_map()