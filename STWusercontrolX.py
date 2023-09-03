# -*- coding: utf-8 -*-
""" STWusercontrol module of the observator project.

This module abstracts remote functions.

Todo:

Note: windows only

"""

import XInput  

import threading
import queue
import logging
import STWobject

class uc(STWobject.stwObject):

    def __init__(self, logger, reverseStick = True):
        super().__init__(logger)
        self.reverseStick = reverseStick
        if self.reverseStick:
            self.log.info("Remote in reverse mode. Not implemented")

    def Init(self):
        self.log.info("Initialize UserControl.")
        return super().Init()

    def Config(self):
        
        self.PollDataQuene = queue.Queue()
        self.exitthread = threading.Event()
        self.getEventThread = threading.Thread(target=self.getEvent, daemon=True)
        self.getEventThread.start()

        self.isConfigured = True

        return super().Config()


    def Shutdown(self):
        self.isConfigured = False

        self.exitthread.set()
        self.getEventThread.join()

        return super().Shutdown()

    def getEvent(self):
        while not self.exitthread.is_set():
            
            for event in XInput.get_events():
                # process first remote only
                if event.user_index != 0:
                    continue

                if event.type == XInput.EVENT_CONNECTED:
                    self.log.info("Remote connected.")

                if event.type == XInput.EVENT_DISCONNECTED:
                    self.log.info("Remote disconnected.")

                if event.type == XInput.BATTERY_LEVEL_LOW:
                    self.log.info("Remote Remote Battery low.")

                if event.type == XInput.EVENT_BUTTON_PRESSED:
                    match event.button:
                        case "A" : 
                            self.PollDataQuene.put('A', block=False)
                        case "B" :
                            self.PollDataQuene.put('B', block=False)
                        case "X" : 
                            self.PollDataQuene.put('X', block=False)
                        case "Y" :
                            self.PollDataQuene.put('Y', block=False)
                        case "LEFT_SHOULDER":
                            self.PollDataQuene.put('S1', block=False)
                        case "RIGHT_SHOULDER":
                            self.PollDataQuene.put('S2', block=False)
                        case  "DPAD_LEFT" :
                            self.PollDataQuene.put('XL',  block=False)
                        case  "DPAD_RIGHT" :
                            self.PollDataQuene.put('XR',  block=False)
                        case  "DPAD_UP" :
                            self.PollDataQuene.put('YU',  block=False)
                        case  "DPAD_DOWN" :
                            self.PollDataQuene.put('YD',  block=False)
                        case  "BACK" :
                            self.PollDataQuene.put('QT',  block=False)

                                                   
                if event.type == XInput.EVENT_BUTTON_RELEASED:
                    match event.button:
                        case  "DPAD_LEFT" :
                            self.PollDataQuene.put('XC',  block=False)
                        case  "DPAD_RIGHT" :
                            self.PollDataQuene.put('XC',  block=False)
                        case  "DPAD_UP" :
                            self.PollDataQuene.put('YC',  block=False)
                        case  "DPAD_DOWN" :
                            self.PollDataQuene.put('YC',  block=False)

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
