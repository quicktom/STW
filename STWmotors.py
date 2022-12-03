# -*- coding: utf-8 -*-
""" STWmotors module of the observator project.

This module abstracts motors functions.

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

class motors(STWobject.stwObject):

    def Init(self):
        self.log.info("Initialize Motors.")
        return super().Init()

