# -*- coding: utf-8 -*-
""" STWcomponents module of the observator project.

This module abstracts stellarium functions.

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

import STWobject, STWsystem, STWastrometry, STWmotors, STWusercontrol, STWstellarium

import time

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

    def Config(self):
        self.log.info("Start configuration phase.")

        self.astro.Config()
        self.uc.Config()
        self.sys.Config()
        self.uc.Config()
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

        loop = True    

        ra_a = 0
        de_a = 0
        while loop:
        # collect data
                         
        # get inputs form user and Stellarium
            remote = self.uc.listen()

            if remote:
                self.log.debug('User remote command ' + remote)
                if remote == 'S2':
                    loop = False

            ret, ra, de  = self.stellarium.ReceiveFromStellarium()
            if ret:
                ra_a = ra
                de_a = de
            
            time.sleep(0.5)

            self.stellarium.SendToStellarium(ra_a, de_a)


        # set outputs motors and stellarium
