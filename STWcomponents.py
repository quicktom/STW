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

class components(STWobject.stwObject):
    def __init__(self, logger):
        super().__init__(logger)

        self.sys        = STWsystem.sys(self.log)
        self.astro      = STWastrometry.astro(self.log)
        self.uc         = STWusercontrol.uc(self.log)
        self.motors     = STWmotors.motors(self.log)
        self.stellarium = STWstellarium.stellarium(self.log)

# start basic initialisation phase
    def Init(self):
        self.log.info("Start basic initialisation phase.")

        self.sys.Init()
        self.astro.Init()
        self.motors.Init()
        self.uc.Init()
        self.stellarium.Init()

    def Config(self):
        self.log.info("Start configuration phase.")

        self.astro.Config()

        return super().Config()

    def PreLoop(self):
        self.log.info("Start preloop phase.")

    def Loop(self):
        self.log.info("Start loop phase.")

        # get inputs form user and Stellarium

        # set outputs motors and stellarium


    def ExitLoop(self):
        self.log.info("Start exit loop phase.")

    def Shutdown(self):
        self.log.info("Start shutdown phase.")
