## --- Runs on Crazyflie 2.0 ---
# **** Enabling stable hovering ******
### Exit using keyboard press in allowed ##

#Date: 11th April 2016

import time
from threading import Thread
import sys

sys.path.append("../lib")
 
import cflib
import cflib.crtp
from cflib.crazyflie import Crazyflie
import signal
 

 
class simpleHover:

    roll = 0
    pitch = 0
    yaw = 0
    thrust = 0

    _stop = 0;
 
    def __init__(self):

        self.crazyflie = Crazyflie()
        cflib.crtp.init_drivers()
 
        # You may need to update this value if your Crazyradio uses a different frequency.
        self.crazyflie.open_link("radio://0/80/250K")
        print "Crazyflie connecting to: radio://0/80/250K"
        self.crazyflie.connected.add_callback(self.connectSetupFinished)

    def connectSetupFinished(self, linkURI):

        print "Crazyflie connected now!"
        #Start two threads
        Thread(target=self.pulse_command).start()

        print "Press C to quit the program at any time"
        while 1:
            try:
                command = raw_input("Set thrust (10001-60000); c quits the program and d starts in fixed torque mode:")

                if (command =='c') or (command == 'C'):
			self.thrust = 0
                    	time.sleep(0.5)				 #To make sure that thrust is actually set to 0
                    	self._stop =  1
                    	print 'Exiting main loop'
                    	time.sleep(1)
                    	self.crazyflie.close_link()
                    	break

                elif (command == 'd') or (command == 'D'):
                    	self.thrust = 35000
                    	time.sleep(1.5) # 1 works
			#cf.param.set_value("flightmode.althold", "True")
			#cf.commander.send_setpoint(0, 0, 0, 32767)
			#while 1:
			#	self.thrust = 32767

                   	print 'Running is constant thrust mode:' 

                elif (self.is_number(command)):
                    	self.thrust = int(command)

                    	if self.thrust == 0:
                        	self.thrust = 0
                    	elif self.thrust <= 10000:
                        	self.thrust = 10001
                    	elif self.thrust > 60000:
                        	self.thrust == 60000

                    	print 'Setting thrust to: %i' %(self.thrust)
                 
                else:
                    	print 'Wrong thrust value: enter a number or c to quit/ d to fixed mode '

            except:
                	print 'Some exception thrown!!', sys.exc_info()[0]

    def is_number(self, input):
        try:
            int(input)
            return True 

        except ValueError:
            return False
                                                          

                
    def pulse_command(self):

        while 1:
            self.crazyflie.commander.send_setpoint(self.roll, self.pitch, self.yaw, self.thrust)
            #self.crazyflie.commander.send_setpoint(0,0,0,20000)
            time.sleep(0.1)
 
        if self._stop==1:
            print "Exception : Quitting"
            return

simpleHover()

