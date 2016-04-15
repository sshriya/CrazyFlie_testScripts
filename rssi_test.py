import sys
sys.path.append("../lib")
sys.path.append("../lib/cflib/drivers")
#from crazyradio import Crazyradio
import crazyradio

radio = crazyradio.Crazyradio()
radio.set_channel(100)
radio.set_data_rate(Crazyradio.DR_250KPS)
#radio.set_mode(Crazyradio.MODE_PRX)
for i in range(0, 100):
    res = radio.receive()
    if res:
        radio.sendAck([i])
    print(res)
radio.close()
