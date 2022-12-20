# -*- coding: utf-8 -*-
""" Top module of the observator project.

This module is the top most of the project and contains the main and the main loop.


"""

import logging, sys

import STWcomponents

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
    SetupLogging(True)
    logger = logging.getLogger(__name__)
    logger.info("Initialize program.")

# basic configuration phase
    comp = STWcomponents.components(logger)

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
 