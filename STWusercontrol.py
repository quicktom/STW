# -*- coding: utf-8 -*-
""" STWusercontrol module of the observator project.

This module abstracts astrometry functions.

Todo:

__author__ = "Thomas Rinder"
__copyright__ = "Copyright 2023, The observator Group"
__credits__ = ["Thomas Rinder"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Thomas Rinder"
__email__ = "thomas.rinder@fh-kiel.de"
__status__ = "alpha"

"""

import STWobject

# windows
import ctypes
ctypes.CDLL('./hidapi/x64/hidapi.dll')

import hid, struct, queue


# ubuntu
# sudo chmod a+rw /dev/hidraw5


class uc(STWobject.stwObject):

    def Init(self):
        self.log.info("Initialize UserControl.")
        return super().Init()

    KEY_RELEASED    = 0
    KEY_A_PRESSED   = 16
    KEY_B_PRESSED   = 1
    KEY_C_PRESSED   = 8
    KEY_D_PRESSED   = 2
    KEY_S1_PRESSED  = 64
    KEY_S2_PRESSED  = 128

    JOY_STICK_AXIS_X_LEFT   = 1
    JOY_STICK_AXIS_X_RIGHT  = 2
    JOY_STICK_AXIS_X_CENTER = 0
    JOY_STICK_AXIS_X_S_IDLE = 4

    JOY_STICK_AXIS_Y_DOWN   = 1
    JOY_STICK_AXIS_Y_UP     = 2
    JOY_STICK_AXIS_Y_CENTER = 0
    JOY_STICK_AXIS_Y_S_IDLE = 4

    def Config(self):
        self.vid  = 1452 
        self.pid  = 12850   
        self.path = b'\\\\?\\HID#{00001124-0000-1000-8000-00805f9b34fb}_VID&000205ac_PID&3232&Col04#8&16f637c6&2&0003#{4d1e55b2-f16f-11cf-88cb-001111000030}'
        #self.path =  b'/dev/hidraw5'

        # game pad
        self.button_A  = self.KEY_RELEASED
        self.button_B  = self.KEY_RELEASED
        self.button_C  = self.KEY_RELEASED
        self.button_D  = self.KEY_RELEASED
        self.button_S1 = self.KEY_RELEASED
        self.button_S2 = self.KEY_RELEASED

        self.JOY_STICK_X = self.JOY_STICK_AXIS_X_CENTER
        self.JOY_STICK_Y = self.JOY_STICK_AXIS_Y_CENTER

        self.JOY_STICK_X_S = self.JOY_STICK_AXIS_X_S_IDLE
        self.JOY_STICK_Y_S = self.JOY_STICK_AXIS_Y_S_IDLE

        self.log.info('Switch on Auvisio game controler and press @+B for game mode!')

        self.PollDataQuene = queue.Queue()

        # try open device
        try:
            self.h = hid.Device(vid = self.vid, pid = self.pid, path = self.path)
        except:
            pass

        self.isConfigured = True

        return super().Config()

    def Shutdown(self):
        self.h.close()
        self.isConfigured = False
        return super().Shutdown()

    def getEvent(self):

        try:
            # fetch event data
            data = self.h.read(size = 9, timeout= 0)
        except:
            # try open device
            try:
                self.h = hid.Device(vid = self.vid, pid = self.pid, path = self.path)
            except:
                pass
            
            return False

        # if event data then decode, serialize and put to quene                    
        if self.decode(data):        
            if self.button_A:
                self.PollDataQuene.put('A', block = False)

            if self.button_B:
                self.PollDataQuene.put('B', block = False)
                
            if self.button_C:
                self.PollDataQuene.put('C', block = False)
            
            if self.button_D:
                self.PollDataQuene.put('D', block = False)
            
            if self.button_S1:
                self.PollDataQuene.put('S1', block = False)
            
            if self.button_S2:
                self.PollDataQuene.put('S2', block = False)
               
            if self.JOY_STICK_X_S == self.JOY_STICK_AXIS_X_LEFT:
                self.PollDataQuene.put('XL',  block = False)
            elif self.JOY_STICK_X_S == self.JOY_STICK_AXIS_X_RIGHT:
                self.PollDataQuene.put('XR',  block = False)
            elif self.JOY_STICK_X_S == self.JOY_STICK_AXIS_X_CENTER:
                self.PollDataQuene.put('XC',  block = False)

            if self.JOY_STICK_Y_S == self.JOY_STICK_AXIS_Y_UP:
                self.PollDataQuene.put('YU',  block = False)
            elif self.JOY_STICK_Y_S == self.JOY_STICK_AXIS_Y_DOWN:
                self.PollDataQuene.put('YD',  block = False)
            elif self.JOY_STICK_Y_S == self.JOY_STICK_AXIS_Y_CENTER:
                self.PollDataQuene.put('YC',  block = False)

        # pull out events from quene till it is empty
        if self.PollDataQuene.empty():
            return False
        else:
            return self.PollDataQuene.get(block=False)

    def decode(self, data):
        if len(data) == 9:
            if data[0] == 4:    
                cdata = struct.unpack("xBBxxBxxx", data)

                X_S = self.JOY_STICK_X
                Y_S = self.JOY_STICK_Y

                # state
                self.JOY_STICK_X = self.JOY_STICK_AXIS_X_RIGHT  if cdata[1] < 64 else self.JOY_STICK_AXIS_X_LEFT if cdata[1] > 192 else self.JOY_STICK_AXIS_X_CENTER
                self.JOY_STICK_Y = self.JOY_STICK_AXIS_Y_UP     if cdata[0] < 64 else self.JOY_STICK_AXIS_Y_DOWN if cdata[0] > 192 else self.JOY_STICK_AXIS_Y_CENTER

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
                self.button_A  = self.KEY_A_PRESSED  if cdata[2] & self.KEY_A_PRESSED  else self.KEY_RELEASED
                self.button_B  = self.KEY_B_PRESSED  if cdata[2] & self.KEY_B_PRESSED  else self.KEY_RELEASED
                self.button_C  = self.KEY_C_PRESSED  if cdata[2] & self.KEY_C_PRESSED  else self.KEY_RELEASED
                self.button_D  = self.KEY_D_PRESSED  if cdata[2] & self.KEY_D_PRESSED  else self.KEY_RELEASED
                self.button_S1 = self.KEY_S1_PRESSED if cdata[2] & self.KEY_S1_PRESSED else self.KEY_RELEASED
                self.button_S2 = self.KEY_S2_PRESSED if cdata[2] & self.KEY_S2_PRESSED else self.KEY_RELEASED

            return True
        else:
            return False

import logging

def main():

    g = uc(logging.getLogger())

    g.Config()
    
    while True:

            ret = g.getEvent()
            if ret:
                print(ret)
                if ret == 'S2':
                    g.Shutdown()

                    return
    

if __name__ == "__main__":
    main()