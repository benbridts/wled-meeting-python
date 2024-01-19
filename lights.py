import json
import urllib.request
import urllib.error
from typing import List, Optional

NIGHT_LIGHT_MINUTES = 5


def show(leds: "List[WLed]", preset: str) -> None:
    for led in leds:
        led.show(preset)


def turn_off(leds: "List[WLed]") -> None:
    for led in leds:
        led.turn_off()


class WLed:
    def __init__(self, ip_address, config):
        self.ip_address = ip_address
        self._saved_state = {}
        self.config = config

    def show(self, state: str) -> None:
        self._set_to_preset(self.config["presets"][state], bri=self.config["brightness"])

    def turn_off(self) -> None:
        self._set_to_preset(on=False)

    def _set_to_preset(self, preset: Optional[int] = None, on: bool = True, bri: Optional[int] = None) -> None:
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
            url=f"http://{self.ip_address}/json/state",
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
            print(f"{self.ip_address}: URLError")
            pass
        except TimeoutError:
            print(f"{self.ip_address}: TimeoutError")
            pass
