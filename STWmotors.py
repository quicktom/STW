# -*- coding: utf-8 -*-
""" STWmotors module of the observator project.

This module abstracts motors functions.

Todo:

"""
import STWobject

class motors(STWobject.stwObject):

    def Init(self):
        self.log.info("Initialize Motors.")
        return super().Init()

