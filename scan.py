# -*- coding: utf-8 -*-

#Test the scanning interface

import sys

sys.path.append("../lib")
import cflib
import cflib.crtp  # noqa


# Initiate the low level drivers
cflib.crtp.init_drivers(enable_debug_driver=False)

print("Scanning interfaces for Crazyflies...")
available = cflib.crtp.scan_interfaces()


print("Crazyflies found:")
for i in available:
    print(i[0])
