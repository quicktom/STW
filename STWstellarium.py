# -*- coding: utf-8 -*-
""" STWstellarium module of the observator project.

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
import STWobject

import struct, socket, select, threading, logging, queue

class stellarium(STWobject.stwObject):

    def Init(self):
        self.log.info("Initialize Stellarium.")

        # self.listening_socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM | socket.SOCK_NONBLOCK)
        # self.listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.listening_socket.bind( ("", 10001) )


        return super().Init()

    def listen():
        pass
