# -*- coding: utf-8 -*-
""" STWastrometry module of the observator project.

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

import spiceypy
from datetime   import datetime
from math       import floor

class astro(STWobject.stwObject):
    
    def Init(self):
        self.log.info("Initialize Astrometry.")
        return super().Init()

    def Config(self):
        spiceypy.furnsh('telescopeLocal.tm')
        return super().Config()

    def Shutdown(self):
        spiceypy.kclear()
        return super().Shutdown()