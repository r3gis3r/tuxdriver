"""
Direct python bindings to driver.
Way easier to integrate for fast prototyping
"""
from ctypes import *
import threading
import time

__author__ = 'r3gis.3r'


TUX_STATE_OPEN = "OPEN"
TUX_STATE_CLOSE = "CLOSE"


class TuxDriver(threading.Thread):
    """
    Helper class to communicate with driver
    """
    def __init__(self):
        super(TuxDriver, self).__init__()
        self._driver = cdll.LoadLibrary("./unix/libtuxdriver.so")
        self._callbacks = []
        self._driver.TuxDrv_ClearCommandStack()
        self._driver.TuxDrv_SetLogLevel(c_uint8(0))

        # Register status callback

        @CFUNCTYPE(None, c_char_p)
        def on_status_cb(status):
            self._on_status_cb(status)
        self._driver.TuxDrv_SetStatusCallback(on_status_cb)

    def run(self):
        # And start running
        self._driver.TuxDrv_Start()

    def stop(self):
        self._driver.TuxDrv_Stop()

    def _on_status_cb(self, status):
        status_structure = self._driver.GetStatusStruct(status)
        print status_structure

    def _on_dongle_connected(self):
        self._driver.TuxDrv_ResetPositions()
        # print self._driver.TuxDrv_GetAllStatusState()
        # print self._driver.TuxDrv_GetStatusName(0)
        # print self._driver.TuxDrv_GetStatusValue(0)
        # print self._driver.TuxDrv_GetStatusState(0)

    def set_mouth_state(self, state, delay=0):
        self._driver.TuxDrv_PerformCommand(c_double(delay), c_char_p("TUX_CMD:MOUTH:%s" % (state,)))


if __name__ == "__main__":
    drv = TuxDriver()
    drv.start()
    time.sleep(5)
    drv._on_dongle_connected()
    drv.set_mouth_state(TUX_STATE_OPEN)
    time.sleep(5)
    drv.set_mouth_state(TUX_STATE_CLOSE)
    drv.stop()