# -*- coding: utf-8 -*-
""" STWcomponents module of the observator project.

This module abstracts stellarium functions.

Todo:

"""

import STWobject, STWsystem, STWastrometry, STWmotors, STWusercontrol, STWstellarium, STWJob

import time

from signal import signal, SIGINT

class components(STWobject.stwObject):
    def __init__(self, logger):
        super().__init__(logger)

        self.sys        = STWsystem.sys(self.log)
        self.astro      = STWastrometry.astro(self.log)
        self.uc         = STWusercontrol.uc(self.log)
        self.motors     = STWmotors.motors(self.log)
        self.stellarium = STWstellarium.stellarium(self.log)

        self.TimeOffsetSec = 0

# start basic initialisation phase
    def Init(self):
        self.log.info("Start basic initialisation phase.")

        self.sys.Init()
        self.astro.Init()
        self.motors.Init()
        self.stellarium.Init()
        self.uc.Init()

        # CTRL-C detection to exit self.Loop
        signal(SIGINT, self.handler)
        self.ControlCDetected = False
        self.log.info("Press CTRL-C to leave loop.")

    def handler(self, signal_received, frame):
        # Handle any cleanup here
        self.log.info("SIGINT or CTRL-C detected.")
        self.ControlCDetected = True

    def Config(self):
        self.log.info("Start configuration phase.")

        self.astro.Config()
        self.uc.Config()
        self.sys.Config()
        self.stellarium.Config()

        # try to get time offset to system time via NTP
        ret = self.sys.GetNtpOffsetSec()
        self.TimeOffsetSec = ret[1]
        if ret[0]:
            self.log.info("Time offset to NTP Server is %3.2fs", self.TimeOffsetSec)
        else:   
            self.log.info("Unable to detect time offset to NTP Server")

        self.telescope_ra = 0
        self.telescope_de = 0

        return super().Config()

    def PreLoop(self):
        self.log.info("Start preloop phase.")

    def ExitLoop(self):
        self.log.info("Start exit loop phase.")

    def Shutdown(self):
        self.log.info("Start shutdown phase.")
        
        self.astro.Shutdown()
        self.uc.Shutdown()
        self.stellarium.Shutdown()

    def Loop(self):
        self.log.info("Start loop phase.")

        ra_a = 0
        de_a = 0

        CurrentEt = self.astro.GetSecPastJ2000TDBNow(offset = self.TimeOffsetSec)

        # send data to stellarium periodic 
        stellariumPeriodicRead = STWJob.STWJob(0.5) # 0.5 secs 
        stellariumPeriodicRead.startJob(CurrentEt)

        stellariumPeriodicSend = STWJob.STWJob(0.5) # 0.5 secs 
        stellariumPeriodicSend.startJob(CurrentEt)

        while not self.ControlCDetected:

            # 
            CurrentEt = self.astro.GetSecPastJ2000TDBNow(offset = self.TimeOffsetSec)

            # get inputs form user and Stellarium
            remote = self.uc.listen()

            if remote:
                self.log.debug('User remote command ' + remote)

#           C   is speed up
#           D   is speed down
#           Y   is telescope lat
#           X   is telescope lon
#           B   is tracking on/off
#           S1  is sync telescope to stellarium reference
#           S2  is change west/east pier alignment

            if stellariumPeriodicRead.doJob(CurrentEt):
                ret, ra, de  = self.stellarium.ReceiveFromStellarium()
                if ret:
                    ra_a = ra
                    de_a = de
            
            # set outputs motors and stellarium
            if stellariumPeriodicSend.doJob(CurrentEt):
                self.stellarium.SendToStellarium(ra_a, de_a)
