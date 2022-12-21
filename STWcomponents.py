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
        self.astroguide = STWastrometry.astroguide(self.log)
        self.uc         = STWusercontrol.uc(self.log)
        self.motors     = STWmotors.motors(self.log)
        self.stellarium = STWstellarium.stellarium(self.log)

        self.TimeOffsetSec = 0

# start basic initialisation phase
    def Init(self):
        self.log.info("Start basic initialisation phase.")

        self.sys.Init()
        self.astro.Init()
        self.astroguide.Init()
        self.motors.Init()
        self.stellarium.Init()
        self.uc.Init()

        # CTRL-C detection to exit self.Loop
        signal(SIGINT, self.handlerSIGINT)
        self.ControlCDetected = False
        self.log.info("Press CTRL-C to leave loop.")

    def handlerSIGINT(self, signal_received, frame):
        self.log.info("SIGINT or CTRL-C detected.")
        self.ControlCDetected = True

    def Config(self):
        self.log.info("Start configuration phase.")

        self.astro.Config()
        self.astroguide.Config()
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
        self.astroguide.Shutdown()
        self.uc.Shutdown()
        self.sys.Shutdown()
        self.stellarium.Shutdown()

    def Loop(self):
        self.log.info("Start loop phase.")

        CurrentEt = self.astro.GetSecPastJ2000TDBNow(offset = self.TimeOffsetSec)

        # loop periodic 
        loopPeriodic = STWJob.STWJob(0.1)           # 0.1 secs
        loopPeriodic.startJob(CurrentEt)

        stellariumPeriodicSend = STWJob.STWJob(0.5) # 0.5 secs 
        stellariumPeriodicSend.startJob(CurrentEt)

        self.astroguide.SetTarget(CurrentEt, 0, 0)

        while not self.ControlCDetected:
            CurrentEt = self.astro.GetSecPastJ2000TDBNow(offset = self.TimeOffsetSec)

            if loopPeriodic.doJob(CurrentEt):

                # get user inputs 
                remote = self.uc.listen()
                if remote:
                    self.log.debug('User remote command ' + remote)

    #           C   is speed up
    #           D   is speed down
    #           Y   is telescope lat
    #           X   is telescope lon
    #           B   is tracking on/off / stop motors
    #           S1  is slew telescope to stellarium target
    #           S2  is sync telescope coords to stellarium reference

                # get stellarium input
                ret, ra, de  = self.stellarium.ReceiveFromStellarium()
                if ret:
                    self.astroguide.SetTarget(CurrentEt, ra, de)
                
                # set stellarium output
                if stellariumPeriodicSend.doJob(CurrentEt):
                    # Simulation reflects target lon, lat
                    self.astroguide.SetActual(CurrentEt, self.astroguide.Target.lon, self.astroguide.Target.lat)

                    self.stellarium.SendToStellarium(self.astroguide.Actual.ra, self.astroguide.Actual.de)
