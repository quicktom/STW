# -*- coding: utf-8 -*-
""" STWobject module of the observator project.

This module abstracts stellarium functions.

Todo:

"""

class stwObject:
        log = None
        isInitialized = False
        isConfigured = False

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


