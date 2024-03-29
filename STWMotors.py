# -*- coding: utf-8 -*-
""" STWmotors module of the observator project.

    Mount level

This module abstracts motors functions.

Todo:

"""
import STWMotorsLowLevel

class mount(STWMotorsLowLevel.STWMotorsLowLevel):

    def __init__(self, logger, comportDevStr):
        self.log = logger
        self.comportDevStr = comportDevStr

    def Init(self):
        # Init defaults
        super().Init(comPort = self.comportDevStr)
        # for safety reasons softstop motors
        self.SoftStopMotors(wait=True)
        # set motors to default angles
        self.Axis0_SetAngle2Zero()
        self.Axis1_SetAngle2Zero()    
        self.log.debug("Mount at telescope angles %f %f", self.Axis0_Angle(), self.Axis1_Angle())
            
    def Shutdown(self):
        self.SoftStopMotors(wait=True)
        super().Shutdown()

    def SetConstantSpeed(self, lonps, latps):
        self.Axis0_Run(lonps)        
        self.Axis1_Run(latps)

    def SoftStopMotors(self, wait = False):
        self.log.debug("Softstop Motors. Wait.")    
        self.Axis0_SoftStop()
        self.Axis1_SoftStop()

        if wait:
            self.log.debug("Wait for halt (blocks program).")       
            self.WaitSoftStop(0)
            self.WaitSoftStop(1)
        
    def CheckErrors(self):
        ret = self.GetErrorStatus(0)
        if bool(ret):
            self.log.error("Motor 0 driver error.")    

        ret = self.GetErrorStatus(1)
        if bool(ret):
            self.log.error("Motor 1 driver error.")    

    def SlewConstantSpeed(self, motor, speedfactor, maxspeed, dir = 1):
        speed = dir*maxspeed*speedfactor 
        if motor == 0:
            self.Axis0_Run(speed)
        else:        
            self.Axis1_Run(speed)