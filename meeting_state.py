import subprocess
from datetime import datetime

WORKING_START_HOUR = 6  # 0 to 23
WORKING_END_HOUR = 19  # 0 to 23


def get_state() -> str:
    if _mic_in_use():
        return "busy"
    if _audio_in_use():
        return "listening"
    if _is_working_hours():
        return "available"
    return "not_working"


def _audio_in_use() -> bool:
    return _number_of_audio_in_use() >= 1


def _mic_in_use() -> bool:
    return _number_of_audio_in_use() >= 2


def _number_of_audio_in_use() -> int:
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


def _is_working_hours() -> bool:
    now = datetime.now()  # should be local time if no tz-info
    if WORKING_START_HOUR <= now.hour < WORKING_END_HOUR:
        return True
    return False
