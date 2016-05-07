#####-------Stable hovering with altitude hold---------#######
# Author : Shriya Shah
# Date : 13th April, 2016

# This program works in indoor environment. Altitude hold mode works nicely. 
# !!!!!!!Thrust depends on battery status!!!!!!!
# Problem : Lot of yaw! 
# Solution : develop a controller (position)

import time
import sys
from threading import Thread
import logging

sys.path.append("../lib")
import cflib  # noqa
from cflib.crazyflie import Crazyflie  # noqa

logging.basicConfig(level=logging.ERROR)


class AltHold:

    def __init__(self, link_uri):

        self._cf = Crazyflie()

        self._cf.connected.add_callback(self._connected)
        self._cf.disconnected.add_callback(self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback(self._connection_lost)

        self._cf.open_link(link_uri)

        print("Connecting to %s" % link_uri)
	

    def _connected(self, link_uri):
        Thread(target=self._ramp_motors).start()

    def _connection_failed(self, link_uri, msg):
        print("Connection to %s failed: %s" % (link_uri, msg))

    def _connection_lost(self, link_uri, msg):
        print("Connection to %s lost: %s" % (link_uri, msg))

    def _disconnected(self, link_uri):
        print("Disconnected from %s" % link_uri)

    def _ramp_motors(self):
        thrust = 36000 #Works at JoBa
        pitch = 0
        roll = 0
        yawrate = 10

        self._cf.commander.send_setpoint(0, 0, 0, 0)

	print("Constant thrust")
        self._cf.commander.send_setpoint(roll, pitch, yawrate, thrust)
        time.sleep(0.75)

	print("Turning on altitude hold")
	self._cf.param.set_value("flightmode.althold", "True")

	start_time = time.time()
	timeC =time.time() -  start_time

	while timeC<3: #wait for 3 seconds
		self._cf.commander.send_setpoint(0, 0, 0, 32767)
		time.sleep(0.1)
		print("hovering!")
		timeC =time.time() -  start_time

	print("Closing link, time taken was: ")
	print timeC

	#close link and execute landing
	self._cf.commander.send_setpoint(0, 0, 0, 0)
	time.sleep(0.1)
	self._cf.close_link()
	


if __name__ == '__main__':
    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)
    # Scan for Crazyflies and use the first one found
    print("Scanning interfaces for Crazyflies...")
    available = cflib.crtp.scan_interfaces()
    print("Crazyflies found:")
    for i in available:
        print(i[0])

    if len(available) > 0:
        le = AltHold(available[0][0])
    else:
        print("No Crazyflies found!")

