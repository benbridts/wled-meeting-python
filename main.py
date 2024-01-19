import os
from time import sleep
from typing import List

from lights import turn_off, show, WLed
from meeting_state import get_state
from util import strtobool

SLEEP_SECONDS = 30
WLED_NODES = {
    "192.168.1.52": {
        "presets": {
            "busy": 3,
            "available": 4,
            "listening": 5,
        },
        "brightness": 31,  # 0 to 256
    },
    "192.168.1.53": {
        "presets": {
            "busy": 9,
            "available": 5,
            "listening": 10,
        },
        "brightness": None,  # 0 to 256
    },
}


def run(once=True, debug: bool = False) -> None:
    leds = [WLed(ip, config) for ip, config in WLED_NODES.items()]
    check_and_show(leds, debug)
    if once:
        return
    while True:
        sleep(SLEEP_SECONDS)
        check_and_show(leds, debug)


def check_and_show(leds: List[WLed], debug: bool = False):
    current_state = get_state()
    if debug:
        print(current_state)
    if current_state == "not_working":
        turn_off(leds)
    else:
        show(leds, current_state)


if __name__ == "__main__":
    # print(get_devices())
    DEBUG = strtobool(os.environ.get("DEBUG", "False"))
    run(once=False, debug=DEBUG)
