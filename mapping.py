import http.client
import os
import socket
import subprocess
import time
import threading
from typing import Optional

from pyodm import Node

node: Node = None
initialized: bool = False
lock: threading.Lock = threading.Lock()

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
                # Tune this to change map quality. Low values = higher quality, 5 is the default
                "orthophoto-resolution": 5
            }
            outputs = [
                "odm_orthophoto/odm_orthophoto.tif",
                "odm_orthophoto/odm_orthophoto.png",
                "odm_orthophoto/odm_orthophoto.kml"
            ]
            task = node.create_task(image_paths, options=options, outputs=outputs, name=f"Mapping-{int(time.time())}")
            print("Task created, waiting for completion...")
            task.wait_for_completion()
            print("Task completed. Downloading results...")
            task.download_assets(output_folder)
            print("Results downloaded")
        except Exception as e:
            print(f"Failed to create or process ODM task: {e}")

if __name__ == "__main__":
    generate_map()