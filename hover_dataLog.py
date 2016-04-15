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
        """ Initialize and run the example with the specified link_uri """
        self.roll = self.pitch = self.yaw = 0
        self.ax = self.ay = self.az = 0
        self.baro = 0


        # Create a Crazyflie object without specifying any cache dirs
        self.crazyflie = Crazyflie()

        # Connect some callbacks from the Crazyflie API
        self.crazyflie.connected.add_callback(self._connected)
        self.crazyflie.disconnected.add_callback(self._disconnected)
        self.crazyflie.connection_failed.add_callback(self._connection_failed)
        self.crazyflie.connection_lost.add_callback(self._connection_lost)

        print("Connecting to %s" % link_uri)

        # Try to connect to the Crazyflie
        self.crazyflie.open_link(link_uri)

        # Variable used to keep main loop occupied until disconnect
        self.is_connected = True

    def _connected(self, link_uri):
        """ This callback is called form the Crazyflie API when a Crazyflie
        has been connected and the TOCs have been downloaded."""
        print("Connected to %s" % link_uri)

        # The definition of the logconfig can be made before connecting
        self._lg_stab = LogConfig(name="Logging", period_in_ms=10)
        self._lg_stab.add_variable("stabilizer.roll", "float")
        self._lg_stab.add_variable("stabilizer.pitch", "float")
        self._lg_stab.add_variable("stabilizer.yaw", "float")
        self._lg_stab.add_variable("acc.x", "float")
        self._lg_stab.add_variable("acc.y", "float")
        self._lg_stab.add_variable("acc.z", "float")
        #self._lg_stab.add_variable("baro.aslLong", "float")
 

        # Adding the configuration cannot be done until a Crazyflie is
        # connected, since we need to check that the variables we
        # would like to log are in the TOC.
        try:
            self.crazyflie.log.add_config(self._lg_stab)
            #self.crazyflie.log.add_config(self._lg_accel)
            # This callback will receive the data
            self._lg_stab.data_received_cb.add_callback(self._stab_log_data)
            #self._lg_accel.data_received_cb.add_callback(self._accel_log_data)
            # This callback will be called on errors
            self._lg_stab.error_cb.add_callback(self._stab_log_error)
            #self._lg_accel.error_cb.add_callback(self._accel_log_error)
            # Start the logging
            self._lg_stab.start()
            #self._lg_accel.start()
        except KeyError as e:
            print("Could not start log configuration,"
                  "{} not found in TOC".format(str(e)))
        except AttributeError:
            print("Could not add Stabilizer log config, bad configuration.")

        # Start a timer to disconnect in 10s
        t = Timer(5, self.crazyflie.close_link)
        #t.start()

    def _stab_log_error(self, logconf, msg):
        """Callback from the log API when an error occurs"""
        print("Error when logging %s: %s" % (logconf.name, msg))

    def _accel_log_error(self, logconf, msg):
        """Callback from the log API when an error occurs"""
        print("Error when logging %s: %s" % (logconf.name, msg))

    def _stab_log_data(self, timestamp, data, logconf):
        """Callback froma the log API when data arrives"""
        #print("[%d][%s]: %s" % (timestamp, logconf.name, data))
        #logging.info("Id={0}, Stabilizer: Roll={1:.2f}, Pitch={2:.2f}, Yaw={3:.2f}, Thrust={4:.2f}".format(ident, data["stabilizer.roll"], data["stabilizer.pitch"], data["stabilizer.yaw"], data["stabilizer.thrust"]))
        #print("[%d][%s]: %.2f" % (timestamp, logconf.name, data["stabilizer.roll"]))
        self.roll =  data["stabilizer.roll"]
        self.pitch =  data["stabilizer.pitch"]
        self.yaw =  data["stabilizer.yaw"]
        self.ax =  data["acc.x"]
        self.ay =  data["acc.y"]
        self.az =  data["acc.z"]
        #self.baro = data["baro.aslLong"]


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
        if (raw_input() == 'c' or raw_input() == 'C'):
            print 'Exiting main loop'
            le.crazyflie.close_link()
            break 

        else:    
            #print "Roll, pitch and yaw values are: "
            print("[%.2f], [%.2f], [%.2f]" % (le.roll, le.pitch, le.yaw))

        time.sleep(0.5)
