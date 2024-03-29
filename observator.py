#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" Top module of the observator project.

This module is the top most of the project and contains the main and the main loop.


"""

import logging, sys, argparse

import STWcomponents

__author__      = "Thomas Rinder"
__copyright__   = "Copyright 2023, Thomas Rinder"
__credits__     = ["Thomas Rinder"]
__license__     = "unlicense"
__version__     = "0.2.0"
__maintainer__  = "Thomas Rinder"
__email__       = "thomas.rinder@fh-kiel.de"
__status__      = "alpha"


defaultComportStr = 'COM4' 

# Configure logger
def SetupLogging(debug = False):
    # setup logging 
    logger = logging.getLogger()

    if debug:
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s | {%(pathname)s:%(lineno)d}', 
                                '%m-%d-%Y %H:%M:%S')
    else:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s', 
                                '%m-%d-%Y %H:%M:%S')

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)

    file_handler = logging.FileHandler('logs.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)

# main entry
def main():
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--debugOff",       help="Print informations only.", action="store_true")
    # if not set EastPier then telescope is in westPier
    parser.add_argument("--EastPier",       help="Set telescope to East pier.", action="store_true")
    parser.add_argument("--comport",        help="Set serial comport device string.", nargs='?', default=defaultComportStr, type=str)
    parser.add_argument("--remoteReverse",  help="Remote in reverse mode.", action="store_true")

    args = parser.parse_args()

    SetupLogging(not args.debugOff)
    logger = logging.getLogger(__name__)
    logger.info("Initialize program.")
    logger.info("------------------------------------------------------")
    logger.info("Author : " + __author__ + "(" + __email__ + ")")
    logger.info("Version: " + __version__ )
    logger.info("------------------------------------------------------")
    logger.info("Program configuration:")
    logger.info("debugOff               : %r", args.debugOff)
    logger.info("westPier               : %r", not args.EastPier)
    logger.info("Comport device string  : %s", args.comport)
    logger.info("Remote in reverse mode : %s", args.remoteReverse)
   
    logger.info("------------------------------------------------------")

# basic configuration phase
    comp = STWcomponents.components(logger, not args.EastPier, args.comport, args.remoteReverse)

# initialization phase
    comp.Init()

# config phase
    comp.Config()

# preloop phase
    comp.PreLoop()

# loop phase
    comp.Loop()

# exit loop phase
    comp.ExitLoop()

# shutdown phase
    comp.Shutdown()
    
    logger.info("Shutdown. Exit program.")

if __name__ == "__main__":
    main()