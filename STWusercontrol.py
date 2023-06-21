# -*- coding: utf-8 -*-
""" STWusercontrol module of the observator project.

This module abstracts remote functions.

Todo:

Note: 

ubuntu: sudo chmod a+rw /dev/hidraw5

"""

# conditional import for windows plattform
import sys
if sys.platform == 'win32':
    import ctypes
    ctypes.CDLL('./hidapi/x64/hidapi.dll')

import threading
import queue
import struct
import logging
import hid
import STWobject

class uc(STWobject.stwObject):

    def __init__(self, logger, reverseStick = True):
        super().__init__(logger)
        self.reverseStick = reverseStick
        if self.reverseStick:
            self.log.info("Remote in reverse mode.")

    def Init(self):
        self.log.info("Initialize UserControl.")
        return super().Init()
    
    KEY_RELEASED = 0
    KEY_A_PRESSED = 16
    KEY_B_PRESSED = 1
    KEY_C_PRESSED = 8
    KEY_D_PRESSED = 2
    KEY_S1_PRESSED = 64
    KEY_S2_PRESSED = 128

    JOY_STICK_AXIS_X_LEFT = 1
    JOY_STICK_AXIS_X_RIGHT = 2
    JOY_STICK_AXIS_X_CENTER = 0
    JOY_STICK_AXIS_X_S_IDLE = 4

    JOY_STICK_AXIS_Y_DOWN = 1
    JOY_STICK_AXIS_Y_UP = 2
    JOY_STICK_AXIS_Y_CENTER = 0
    JOY_STICK_AXIS_Y_S_IDLE = 4

    REMOTE_VID = 1452
    REMOTE_PID = 12850

    def Config(self):
        
        dev = self.DiscoverRemoteDevString(self.REMOTE_VID, self.REMOTE_PID)
        if dev:
            self.path = dev
        else:
            self.log.fatal("Remote not found.")
            quit()

        self.button_A = self.KEY_RELEASED
        self.button_B = self.KEY_RELEASED
        self.button_C = self.KEY_RELEASED
        self.button_D = self.KEY_RELEASED
        self.button_S1 = self.KEY_RELEASED
        self.button_S2 = self.KEY_RELEASED

        self.XCOORD = 0
        self.XCOORD_CHANGED = False
        self.YCOORD = 0
        self.YCOORD_CHANGED = False

        self.JOY_STICK_X = self.JOY_STICK_AXIS_X_CENTER
        self.JOY_STICK_Y = self.JOY_STICK_AXIS_Y_CENTER

        self.JOY_STICK_X_S = self.JOY_STICK_AXIS_X_S_IDLE
        self.JOY_STICK_Y_S = self.JOY_STICK_AXIS_Y_S_IDLE
        
        self.log.info('Switch on controler and press @+B for game mode.')

        self.h = False
        self.supressretry = False

        self.PollDataQuene = queue.Queue()
        self.exitthread = threading.Event()
        self.getEventThread = threading.Thread(target=self.getEvent, daemon=True)
        self.getEventThread.start()

        self.isConfigured = True

        return super().Config()

    def DiscoverRemoteDevString(self, vid, pid):
        s = hid.enumerate()
        for device in s:
            if device['vendor_id'] == vid and device['product_id'] == pid and device['usage'] == 5:
                return device['path'] 

        self.log.fatal("Remote HZ2746 was not found.")
        self.log.fatal("Switch on remote and check bluetooth settings.")

        return False    


    def Shutdown(self):
        self.isConfigured = False

        self.exitthread.set()
        self.getEventThread.join()

        return super().Shutdown()

    def getEvent(self):

        while not self.exitthread.is_set():
            try:
                if self.h:
                    data = self.h.read(size=9, timeout=0) 
                else:
                    # device is not open or something
                    raise Exception
            except:
                # try open device
                if not self.supressretry:
                    self.log.info("Try to open HID device.")
                try:
                    self.h = hid.Device(path=self.path)
                except:
                    # if can not open device then try again
                    self.h = False
                    self.supressretry = True
                    continue
                else:
                    # ToDo Device can be opened but may not be present actually ?
                    self.log.info(
                        "HID device is open. Press @ + B for game mode.")
                    self.supressretry = False
                    continue
            else:
                # if data is empty then try again
                if not data:
                    continue

            # if event data then decode, serialize and put to quene
            if self.decode(data):
                if self.button_A:
                    self.PollDataQuene.put('A', block=False)

                if self.button_B:
                    self.PollDataQuene.put('B', block=False)

                if self.button_C:
                    self.PollDataQuene.put('C', block=False)

                if self.button_D:
                    self.PollDataQuene.put('D', block=False)

                if self.button_S1:
                    self.PollDataQuene.put('S1', block=False)

                if self.button_S2:
                    self.PollDataQuene.put('S2', block=False)

                if self.JOY_STICK_X_S == self.JOY_STICK_AXIS_X_LEFT:
                    self.PollDataQuene.put('XL',  block=False)
                elif self.JOY_STICK_X_S == self.JOY_STICK_AXIS_X_RIGHT:
                    self.PollDataQuene.put('XR',  block=False)
                elif self.JOY_STICK_X_S == self.JOY_STICK_AXIS_X_CENTER:
                    self.PollDataQuene.put('XC',  block=False)

                if self.JOY_STICK_Y_S == self.JOY_STICK_AXIS_Y_UP:
                    self.PollDataQuene.put('YU',  block=False)
                elif self.JOY_STICK_Y_S == self.JOY_STICK_AXIS_Y_DOWN:
                    self.PollDataQuene.put('YD',  block=False)
                elif self.JOY_STICK_Y_S == self.JOY_STICK_AXIS_Y_CENTER:
                    self.PollDataQuene.put('YC',  block=False)

                # controler coords not good at all
                # if self.XCOORD_CHANGED:
                #     self.PollDataQuene.put('X' + str(self.XCOORD),  block = False)

                # if self.YCOORD_CHANGED:
                #     self.PollDataQuene.put('Y' + str(self.YCOORD),  block = False)


    def decode(self, data):
        if len(data) == 9:
            if data[0] == 4:
                cdata = struct.unpack("xBBxxBxxx", data)

                X_S = self.JOY_STICK_X
                Y_S = self.JOY_STICK_Y

                if self.reverseStick:
                    Ypos = 255 - cdata[0]
                    XPos = 255 - cdata[1]
                else:
                    Ypos = cdata[0]
                    XPos = cdata[1]

                # state
                self.JOY_STICK_X = self.JOY_STICK_AXIS_X_RIGHT if XPos < 64 else self.JOY_STICK_AXIS_X_LEFT if XPos > 192 else self.JOY_STICK_AXIS_X_CENTER
                self.JOY_STICK_Y = self.JOY_STICK_AXIS_Y_UP    if Ypos < 64 else self.JOY_STICK_AXIS_Y_DOWN if Ypos > 192 else self.JOY_STICK_AXIS_Y_CENTER

                # stick coordinates
                # if self.XCOORD != cdata[1]:
                #     self.XCOORD = cdata[1]
                #     self.XCOORD_CHANGED = True
                # else:
                #     self.XCOORD_CHANGED = False

                # if self.YCOORD != cdata[0]:
                #     self.YCOORD = cdata[0]
                #     self.YCOORD_CHANGED = True
                # else:
                #     self.YCOORD_CHANGED = False

                # one shot detect on joystick
                if X_S != self.JOY_STICK_X:
                    self.JOY_STICK_X_S = self.JOY_STICK_X
                else:
                    self.JOY_STICK_X_S = self.JOY_STICK_AXIS_X_S_IDLE

                if Y_S != self.JOY_STICK_Y:
                    self.JOY_STICK_Y_S = self.JOY_STICK_Y
                else:
                    self.JOY_STICK_Y_S = self.JOY_STICK_AXIS_Y_S_IDLE

                # one shot already
                self.button_A = self.KEY_A_PRESSED if cdata[2] & self.KEY_A_PRESSED else self.KEY_RELEASED
                self.button_B = self.KEY_B_PRESSED if cdata[2] & self.KEY_B_PRESSED else self.KEY_RELEASED
                self.button_C = self.KEY_C_PRESSED if cdata[2] & self.KEY_C_PRESSED else self.KEY_RELEASED
                self.button_D = self.KEY_D_PRESSED if cdata[2] & self.KEY_D_PRESSED else self.KEY_RELEASED
                self.button_S1 = self.KEY_S1_PRESSED if cdata[2] & self.KEY_S1_PRESSED else self.KEY_RELEASED
                self.button_S2 = self.KEY_S2_PRESSED if cdata[2] & self.KEY_S2_PRESSED else self.KEY_RELEASED

            return True
        else:
            return False

    def listen(self):
        # pull out events from quene till it is empty
        if self.PollDataQuene.empty():
            return False
        else:
            return self.PollDataQuene.get(block=False)
        
    def clear(self):
        with self.PollDataQuene.mutex:
            self.PollDataQuene.queue.clear()        

def main():

    g = uc(logging.getLogger())

    g.Config()

    while True:

        ret = g.listen()
        if ret:
            print(ret)
            if ret == 'S2':
                g.Shutdown()
                return


if __name__ == "__main__":
    main()
