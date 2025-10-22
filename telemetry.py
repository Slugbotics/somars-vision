import util
import time
from enum import Enum
from ultralytics.engine.results import Results # type: ignore

class ObjClasses(Enum):
    MANNEQUIN = 0
    TENT = 1

x_offset: list[float] = []
y_offset: list[float] = []
object_class: list[str] = []
latency_list: list[float] = []

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
        # TODO: Send values to main computer