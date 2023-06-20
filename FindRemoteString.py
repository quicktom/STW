#import ctypes
#ctypes.CDLL('./hidapi/x64/hidapi.dll')

# sudo apt install libhidapi-dev

import hid

s = hid.enumerate()
for device in s:
    if device['vendor_id'] == 1452:
        print(f"0x{device['vendor_id']:04x}:0x{device['product_id']:04x} {device['product_string']}")
        if device['usage'] == 5:
            print(device['path'] )

#h = hid.Device( path=  b'/dev/hidraw5')
# #print(h)

