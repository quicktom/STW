# -*- coding: utf-8 -*-
""" STWsystem module of the observator project.

This module abstracts system functions.

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

import ntplib

class sys(STWobject.stwObject):

    def Init(self):
        self.log.info("Initialize STWsystem.")
        
        return super().Init()

    def GetNtpOffsetSec(self):
        try:
            response = ntplib.NTPClient().request('europe.pool.ntp.org', version=3)
        except:
            return [False, 0]
        # if positive offset then server is offset secs ahead of system time
        return [True, response.offset]

import logging

def main():

    g = sys(logging.getLogger())

    g.Config()
    
    print(g.GetNtpOffsetSec())
    

if __name__ == "__main__":
    main()