"""
Direct python bindings to driver.
Way easier to integrate for fast prototyping
"""
import logging
from ctypes import *
import threading
import time

__author__ = 'r3gis.3r'


def _tux_status_to_dict(status=""):
    result = {
        'name': "None",
        'value': None,
        'delay': 0.0,
        'type': 'string'
    }

    try:
        result['name'], result['type'], result['value'], result['delay'] = status.split(":")
    except ValueError:
        logging.error("Cannot parse %s", status)
        return result

    if result['type'] in ['uint8', 'int8', 'int', 'float', 'bool']:
        result['value'] = eval(result['value'])

    return result


class TuxDriver(threading.Thread):
    """
    Helper class to communicate with driver
    """
    def __init__(self):
        super(TuxDriver, self).__init__()
        self._driver = cdll.LoadLibrary("./unix/libtuxdriver.so")
        self._callbacks = []
        self._driver.TuxDrv_SetLogLevel(c_uint8(0))

        # Register status callback
        def on_status_cb(status):
            self._on_status_cb(status)

        # Need to be assigned to avoid GC
        self._internal_status_cb = CFUNCTYPE(None, c_char_p)(on_status_cb)
        self._driver.TuxDrv_SetStatusCallback(self._internal_status_cb)

    def run(self):
        # And start running
        self._driver.TuxDrv_Start()

    def stop(self):
        self._driver.TuxDrv_Stop()

    def _on_status_cb(self, status):
        status_structure = _tux_status_to_dict(status)
        for callback in self._callbacks:
            callback(status_structure)
        print status_structure

    def _on_dongle_connected(self):
        self._driver.TuxDrv_ResetPositions()

    def send_command(self, command, delay=0.0):
        self._driver.TuxDrv_PerformCommand(c_double(delay), c_char_p(str(command)))
        # self._driver.TuxDrv_Mouth_cmd_off()


# List of commands

class TuxCommand(object):
    class_tokens = []

    def __init__(self, *args):
        self.command_tokens = list(args)

    def __repr__(self):
        cmd = ["TUX_CMD"]
        cmd.extend([str(c) for c in self.class_tokens])
        cmd.extend([str(c) for c in self.command_tokens])
        return ":".join(cmd)


TUX_STATE_OPEN = "OPEN"
TUX_STATE_CLOSE = "CLOSE"
TUX_STATE_UP = "UP"
TUX_STATE_DOWN = "DOWN"

# Commands, class are base instances for each primitive, but shortcuts also exists
MouthCommand = type("MouthCommand", (TuxCommand,), {"class_tokens": ["MOUTH"]})
CMD_MOUTH_OPEN = MouthCommand(TUX_STATE_OPEN)
CMD_MOUTH_CLOSE = MouthCommand(TUX_STATE_CLOSE)
EyesCommand = type("EyesCommand", (TuxCommand,), {"class_tokens": ["EYES"]})
CMD_EYES_OPEN = EyesCommand(TUX_STATE_OPEN)
CMD_EYES_CLOSE = EyesCommand(TUX_STATE_CLOSE)
FlippersCommand = type("FlippersCommand", (TuxCommand,), {"class_tokens": ["FLIPPERS"]})
CMD_FLIPPERS_UP = FlippersCommand(TUX_STATE_UP)
CMD_FLIPPERS_DOWN = FlippersCommand(TUX_STATE_DOWN)
SpinningCommand = type("SpinningCommand", (TuxCommand,), {"class_tokens": ["SPINNING"]})


if __name__ == "__main__":
    drv = TuxDriver()
    drv.start()
    time.sleep(1)
    drv._on_dongle_connected()
    time.sleep(2)

    drv.send_command(CMD_MOUTH_OPEN)
    # drv.send_command(SpinningCommand("RIGHT_ON", 1))
    time.sleep(3)
    drv.send_command(CMD_FLIPPERS_UP)
    # drv.send_command(CMD_MOUTH_OPEN, delay=0.4)
    time.sleep(2)
    drv.stop()