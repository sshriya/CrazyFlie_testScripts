##---Data Logging in Error detection mode -------
# all data can be logged by making different calls

#Date: March 26, 2016

import sys
import logging
import time
from threading import Timer

sys.path.append("../lib")
import cflib.crtp  # noqa
from cfclient.utils.logconfigreader import LogConfig  # noqa
from cfclient.utils.logconfigreader import LogVariable
from cflib.crazyflie import Crazyflie  # noqa

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)


class LogData:


    def __init__(self, link_uri):

        self.thrust = 10001
        self.roll = self.pitch = self.yaw = 0

        #Sensors being monitored
        self.r = self.p = self.y = 0
        self.ax = self.ay = self.az = 0
        self.baro = 0


        # Create a Crazyflie object without specifying any cache dirs
        self.crazyflie = Crazyflie()

        # The definition of the logconfig 
        self._lg_stab = LogConfig(name="Logging", period_in_ms=10)
        self._lg_stab.add_variable("stabilizer.roll", "float")
        self._lg_stab.add_variable("stabilizer.pitch", "float")
        self._lg_stab.add_variable("stabilizer.yaw", "float")
        self._lg_stab.add_variable("acc.x", "float")
        self._lg_stab.add_variable("acc.y", "float")
        self._lg_stab.add_variable("acc.z", "float")
        #self._lg_stab.add_variable("baro.aslLong", "float")

        # Connect some callbacks from the Crazyflie API
        self.crazyflie.connected.add_callback(self._connected)
        self.crazyflie.disconnected.add_callback(self._disconnected)
        self.crazyflie.connection_failed.add_callback(self._connection_failed)
        self.crazyflie.connection_lost.add_callback(self._connection_lost)

        print("Connecting to %s" % link_uri)

        # Try to connect to the Crazyflie
        self.crazyflie.open_link(link_uri)

        # Variable used to keep main loop occupied until disconnect
        self.is_connected = False

    def _connected(self, link_uri):

        print("Connected to %s" % link_uri)
        self.crazyflie.is_connected = True

        #create a thread that published the set points
        #Thread(target=self.pulse_command).start()

        # Adding the configuration 
        try:
            #self.crazyflie.log.add_config(self._lg_stab)
            # This callback will receive the data
            #self._lg_stab.data_received_cb.add_callback(self._stab_log_data)
            # This callback will be called on errors
            #self._lg_stab.error_cb.add_callback(self._stab_log_error)
            # Start the logging
            #self._lg_stab.start()
	    print "yay"
            Thread(target=self.pulse_command).start()
	    print "Hello I am out of "

        except KeyError as e:
            print("Could not start log configuration,"
                  "{} not found in TOC".format(str(e)))
        except AttributeError:
            print("Could not add Stabilizer log config, bad configuration.")

        # Start a timer to disconnect in 10s
        #t = Timer(5, self.crazyflie.close_link)
        #t.start()

    def _stab_log_error(self, logconf, msg):
        """Callback from the log API when an error occurs"""
        print("Error when logging %s: %s" % (logconf.name, msg))

    def _accel_log_error(self, logconf, msg):
        """Callback from the log API when an error occurs"""
        print("Error when logging %s: %s" % (logconf.name, msg))

    def _stab_log_data(self, timestamp, data, logconf):
        """Callback from the log API when data arrives"""
        self.r =  data["stabilizer.roll"]
        self.p =  data["stabilizer.pitch"]
        self.y =  data["stabilizer.yaw"]
        self.ax =  data["acc.x"]
        self.ay =  data["acc.y"]
        self.az =  data["acc.z"]
        #self.baro = data["baro.aslLong"]
	print self.ax


    def _connection_failed(self, link_uri, msg):
        """Callback when connection initial connection fails (i.e no Crazyflie
        at the speficied address)"""
        print("Connection to %s failed: %s" % (link_uri, msg))
        self.is_connected = False

    def _connection_lost(self, link_uri, msg):
        """Callback when disconnected after a connection has been made (i.e
        Crazyflie moves out of range)"""
        print("Connection to %s lost: %s" % (link_uri, msg))

    def _disconnected(self, link_uri):
        """Callback when the Crazyflie is disconnected (called in all cases)"""
        print("Disconnected from %s" % link_uri)
        self.is_connected = False

    def pulse_command(self):
	print 'in pulse_command'
        self.crazyflie.commander.send_setpoint(self.roll, self.pitch, self.yaw, self.thrust)
            #self.crazyflie.commander.send_setpoint(0,0,0,20000)
        time.sleep(0.1)
 
   


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
        le = LogData(available[0][0])
    else:
        print("No Crazyflies found, cannot run example")

    # The Crazyflie lib doesn't contain anything to keep the application alive,
    # so this is where your application should do something. In our case we
    # are just waiting until we are disconnected.
    while le.is_connected:
        command = raw_input("Press C to stop: ")
        if (command == 'c' or command == 'C'):
            le.thrust = 0
            time.sleep(0.5)
            print 'Exiting main loop'
            le.crazyflie.close_link()
            break 

        else:   
            #print "Roll, pitch and yaw values are: "
            #print("[%.2f], [%.2f], [%.2f]" % (le.r, le.p, le.y))

            time.sleep(0.5)
