# -*- coding: utf-8 -*-
""" STWobject module of the observator project.

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

class stwObject:
        log = None
        isInitialized = False

        def __init__(self, logger):
            self.log = logger

        def Init(self):
            self.isInitialized = True

        def Config(self):
            pass

        def LoadConfig(self, fname):
            pass 

        def SaveConfig(self, fname, config):
            pass

        def InitializeFrom(self, config):
            pass

        def Shutdown(self):
            pass



