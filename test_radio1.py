#!/usr/bin/env python
import sys
import time

sys.path.append("../lib/cflib/drivers")
import crazyradio
sys.path.append("../lib")
import cflib
import cflib.crtp  # noqa
from cflib.crazyflie import Crazyflie

# Initiate the low level drivers
#crazyflie = Crazyflie()
cr = crazyradio.Crazyradio()
#cflib.crtp.init_drivers(enable_debug_driver=False)

#print("Scanning interfaces for Crazyflies...")
#available = cflib.crtp.scan_interfaces()
'''
print("Crazyflies found:")
for i in available:
    print(i[0])

crazyflie.open_link("radio://0/80/250K")
print "Crazyflie connecting to: radio://0/80/250K"
'''


cr.set_channel(80)
cr.set_data_rate(cr.DR_250KPS)

for i in range(0, 100):
    res = cr.send_packet((0xff,))
    if res:
    	print res
        #cr.sendAck([i])
    #print(res)
cr.close()
#cr.set_mode(cr.MODE_PRX)

'''
while 1:
	res = cr.send_packet([0xff, ])
	if res.ack:
		print "got data"

	else:	
		print "no data"
	#print res.ack
	#print res.data
'''

