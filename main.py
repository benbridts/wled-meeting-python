import os
import subprocess
import urllib.request
import urllib.error

import json
from time import sleep
from datetime import datetime
from typing import Optional

SLEEP_SECONDS = 30
NIGHT_LIGHT_MINUTES = 5
WLED_NODES = {
    "192.168.1.84": {
        "presets": {
            "busy": 3,
            "available": 4,
            "listening": 5,
        },
        "brightness": 31  # 0 to 256
    },
    "192.168.1.101": {
        "presets": {
            "busy": 9,
            "available": 5,
            "listening": 10,
        },
        "brightness": None  # 0 to 256
    },
}

WORKING_START_HOUR = 6  # 0 to 23
WORKING_END_HOUR = 19  # 0 to 23


def run(once=True, debug: bool = False) -> None:
    check_and_show(debug)
    if once:
        return
    while True:
        sleep(SLEEP_SECONDS)
        check_and_show(debug)


def check_and_show(debug: bool = False):
    if audio_in_use_twice():
        if debug:
            print("busy")
        show("busy")
    elif audio_in_use():
        if debug:
            print("listening")
        show("listening")
    elif working_hours():
        if debug:
            print("available")
        show("available")
    else:
        if debug:
            print("not working")
        turn_off()


def show(state: str) -> None:
    for ip, config in WLED_NODES.items():
        set_led_to_preset(ip, config["presets"][state], bri=config["brightness"])


def turn_off() -> None:
    for ip, config in WLED_NODES.items():
        set_led_to_preset(ip, on=False)


def number_of_audio_in_use() -> int:
    r = subprocess.run(
        "ioreg -c AppleUSBAudioEngine -r | grep IOAudioEngineState || true",
        capture_output=True,
        check=True,
        shell=True,
        text=True,
    )
    items_in_use = 0
    for line in r.stdout.splitlines():
        if line[-1] == "1":
            items_in_use += 1
    return items_in_use


def audio_in_use() -> bool:
    return number_of_audio_in_use() >= 1


def audio_in_use_twice() -> bool:
    return number_of_audio_in_use() >= 2


def working_hours() -> bool:
    now = datetime.now()  # should be local time if no tz-info
    if WORKING_START_HOUR <= now.hour < WORKING_END_HOUR:
        return True
    return False


def set_led_to_preset(ip: str, preset: Optional[int] = None, on: bool = True, bri: Optional[int] = None) -> None:
    optional_kwargs = {}
    if on:
        # set night light, so light turns off if script is not running anymore
        optional_kwargs["nl"] = {
            "on": True,
            "dur": NIGHT_LIGHT_MINUTES,  # minutes
            "mode": 0,  # 0: instant, 1: fade, 2: color fade, 3: sunrise
            "tbri": 0,
        }
    req = urllib.request.Request(
        url=f"http://{ip}/json/state",
        data=json.dumps({"on": on, "ps": preset, "bri": bri, **optional_kwargs}).encode("UTF-8"),
        method="POST",
    )
    req.add_header("Content-Type", "application/json")
    # should get an instant response on the local network
    # we do not care about the response
    try:
        with urllib.request.urlopen(req, timeout=2) as _:
            pass
    except urllib.error.URLError:
        print(f"{ip}: URLError")
        pass
    except TimeoutError:
        print(f"{ip}: TimeoutError")
        pass


def strtobool(s: str) -> bool:
    s = s.lower()
    if s in ("y", "yes", "t", "true", "on", "1"):
        return True
    if s in ("n", "no", "f", "false", "off", "0"):
        return False
    raise ValueError(f"invalid truth value {s}")

# def get_devices() -> list[str]:
#     r = subprocess.run(
#         ["ioreg", "-c" "AppleUSBAudioEngine", "-r"],
#         capture_output=True,
#         check=True,
#         text=True,
#     )
#     json_string = '['
#     in_dict = False
#     for line in r.stdout.splitlines():
#         if '+-o' in line:
#             continue  # not interested in the tree
#         line = line.lstrip(' |')  # remove space and |
#         if line == '}':
#             in_dict = True
#         if line == '}':
#             in_dict = False
#         json_string += line
#         if not in_dict:
#
#             json_string += '\n'
#
#     json_string += '{}]'
#     print(json_string)
#     return json.loads(json_string)


if __name__ == "__main__":
    # print(get_devices())
    DEBUG = strtobool(os.environ.get("DEBUG", "False"))
    run(once=False, debug=DEBUG)
