
import time
import sys
from threading import Thread
import logging
import numpy as np 
from math import sin,cos 

sys.path.append("../lib")
import cflib  # noqa
from cflib.crazyflie import Crazyflie  # noqa
import cflib.crtp  # noqa
from cfclient.utils.logconfigreader import LogConfig  # noqa
from cfclient.utils.logconfigreader import LogVariable
from cflib.crazyflie import Crazyflie  # noqa
logging.basicConfig(level=logging.ERROR)

class MotorRampExample:
    thrust = 0
    ax = 0 
    ay=0
    vx =0
    vy=0
    p = 0
    y=0
    px=0
    py=0
    kpx=100
    kpy=100
    prevTime=0
    dt=0
    accCheck = True
    accxInit=0
    accyInit=0 
    def __init__(self, link_uri):
        self._cf = Crazyflie()

	#adding the logging parameter
        print("Connecting to %s" % link_uri)
	self._lg_stab = LogConfig(name="Logging", period_in_ms=10)
        self._lg_stab.add_variable("stabilizer.roll", "float")
        self._lg_stab.add_variable("stabilizer.pitch", "float")
        self._lg_stab.add_variable("stabilizer.yaw", "float")
        self._lg_stab.add_variable("acc.x", "float")
        self._lg_stab.add_variable("acc.y", "float")
        self._lg_stab.add_variable("acc.z", "float")
	self._cf.connected.add_callback(self._connected)
        self._cf.disconnected.add_callback(self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback(self._connection_lost)
	
        self._cf.open_link(link_uri)
    def _connected(self, link_uri):
	self.thrust = 10003
	self.prevTime = time.time()
	self._cf.log.add_config(self._lg_stab)
        # This callback will receive the data
        self._lg_stab.data_received_cb.add_callback(self._stab_log)
        # This callback will be called on errors
        #self._lg_stab.error_cb.add_callback(self._stab_log_error)
        # Start the logging
        self._lg_stab.start()
        Thread(target=self._ramp_motors).start()

    def _connection_failed(self, link_uri, msg):
        """Callback when connection initial connection fails (i.e no Crazyflie
        at the specified address)"""
        print("Connection to %s failed: %s" % (link_uri, msg))
    def _stab_log(self, timestamp, data, logconf):
        """Callback from the log API when data arrives"""
        self.r =  data["stabilizer.roll"]
        self.p =  data["stabilizer.pitch"]
        self.y =  data["stabilizer.yaw"]
	if self.accCheck:
		self.accxInit = data["acc.x"]
		self.accyInit = data["acc.y"]
		self.ax = 0#self.accxInit
		self.ay = 0# self.accyInit
		self.accCheck = False
		print "Hello I am here"
	else:	
        	self.ax =  data["acc.x"] - self.accxInit
        	self.ay =  data["acc.y"] - self.accyInit
        	self.az =  data["acc.z"]
        	self.dt =time.time() -  self.prevTime
	
	self.vx = self.vx + self.ax * self.dt
        self.vy = self.vy + self.ay * self.dt

	self.px = self.px + self.vx*self.dt
	self.py = self.py + self.vy*self.dt

	print("ax: {} ay: {}".format(self.ax, self.ay))
        print("vx: {} vy: {}".format(self.vx, self.vy))
        print("px: {} py: {}".format(self.px, self.py))

	self.prevTime = time.time()

    def _connection_lost(self, link_uri, msg):
        """Callback when disconnected after a connection has been made (i.e
        Crazyflie moves out of range)"""
        print("Connection to %s lost: %s" % (link_uri, msg))

    def _disconnected(self, link_uri):
        """Callback when the Crazyflie is disconnected (called in all cases)"""
        print("Disconnected from %s" % link_uri)

    def _ramp_motors(self):
        thrust_mult = 1
        thrust_step = 500
        pitch = 0
        roll = 0
        yawrate = 0
        # Unlock startup thrust protection
        self._cf.commander.send_setpoint(0, 0, 0, 0)
        start_time = time.time()
	timeC =time.time() -  start_time

	while timeC<2: #wait for 3 seconds
		#R = np.array([[cos(self.y),-sin(self.y)],[sin(self.y),cos(self.y)]])
            	#acc = np.array([[-self.ax],[-self.ay]])
		#print("p: {}".format(self.p))
            	#angles = np.dot(R,acc)
		#print("angles: {}".format(angles))
		#self._cf.commander.send_setpoint(self.kpx*acc[0], self.kpy*acc[1], 0, 33000)
		#self._cf.commander.send_setpoint(0, 2*self.p, 0, 34000)

		time.sleep(0.01)
		#print("hovering!")
		timeC =time.time() -  start_time

	print("Closing link, time taken was: ")

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
        le = MotorRampExample(available[0][0])
    else:

        print("No Crazyflies found, cannot run example")
