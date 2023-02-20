#!/usr/bin/python3

"""
    Protocol layer to the module STWMicroController.

    Angle level.

    Implement low level function of motor movement.
"""

import STWMicroController

class STWMotorsLowLevel(STWMicroController.board):
    # mount specific  ALT7
    #

    # axis "1" is declination 
    # gear ratio from datasheet
    
    STEPS_PER_REV_0  = 270*62.500*100               # steps per revolution
    STEPS_PER_REV_1  = 210*83.333*100               # steps per revolution
    
    DEGS_PER_STEP_0  = 360.0/STEPS_PER_REV_0        # degrees / steps
    DEGS_PER_STEP_1  = 360.0/STEPS_PER_REV_1        # degrees / steps

    STEPS_PER_DEG_0  = 1.0/DEGS_PER_STEP_0          # steps / degress
    STEPS_PER_DEG_1  = 1.0/DEGS_PER_STEP_1          # steps / degress

    def StepsPerAngle(self, motorId, angle):
        if motorId == 0:
            return  angle*self.STEPS_PER_DEG_0 
        else:
            return  angle*self.STEPS_PER_DEG_1 

    def AnglePerSteps(self, motorId, steps):
        if motorId == 0:
            return  steps*self.DEGS_PER_STEP_0 
        else:
            return  steps*self.DEGS_PER_STEP_1 
        
    #
    # final mount driver low level driver
    #

    # slew absolute to degree
    def Axis0_SlewTo(self, angle):      
        return self.GotoPosCmdDir(0, self.StepsPerAngle(0, angle))

    def Axis1_SlewTo(self, angle):
        return self.GotoPosCmdDir(1, self.StepsPerAngle(1, angle))

    # slew absolute increment to degree
    def Axis0_SlewIncTo(self, deginc):
        self.logger.debug("Axis0_SlewIncTo %f degs", deginc)
        return self.MoveCmd(0, self.StepsPerAngle(0, deginc))

    def Axis1_SlewIncTo(self, deginc):
        self.logger.debug("Axis1_SlewIncTo %f ", deginc)
        return self.MoveCmd(1, self.StepsPerAngle(1, deginc))

    # run at constant degrees per sec
    def Axis0_Run(self, angle_per_s):
        stepsps = self.StepsPerAngle(0, angle_per_s)

        # actual angle_per_s and its error to angle_per_s
        actual = self.Axis0_RunActualSpeed(angle_per_s)   
        error = actual - angle_per_s        
        
        self.log.debug("Axis0_Run %f degs/s (actual %f degs/s, error %f(?) arcsecs/h)", angle_per_s, actual, error*3600*60*60)

        return self.RunCmd(0, stepsps)

    # get actual speed degrees per sec (estimate)
    def Axis0_RunActualSpeed(self, angle_per_s):
        return self.AnglePerSteps(0, self.SpeedReg2StepsHz(self.StepsHz2SpeedReg(self.StepsPerAngle(0, angle_per_s))))

    def Axis1_Run(self, angle_per_s):
        self.log.debug("Axis1_Run %f degs/s", angle_per_s)
        return self.RunCmd(1, self.StepsPerAngle(1, angle_per_s))

    def Axis0_Angle(self):
        return self.GetPosCmd(0) * self.DEGS_PER_STEP_0

    def Axis1_Angle(self):
        return self.GetPosCmd(1) * self.DEGS_PER_STEP_1

    def Axis0_SetAngle(self, angle):
        return self.SetPosCmd(0, angle*self.STEPS_PER_DEG_0)

    def Axis1_SetAngle(self, angle):
        return self.SetPosCmd(1, angle*self.STEPS_PER_DEG_1)
        
    # soft stop movement 
    def Axis0_SoftStop(self):
        self.log.debug("Axis0_SoftStop")
        return self.SoftStop(0)

    def Axis1_SoftStop(self):
        self.log.debug("Axis1_SoftStop")
        return self.SoftStop(1)

    # hard stop movement
    def Axis0_HardStop(self):
        self.log.critical("Axis0_HardStop")
        return self.HardStop(0)

    def Axis1_HardStop(self):
        self.log.critical("Axis1_HardStop")
        return self.HardStop(1)

    # set angle to zero
    def Axis0_SetAngle2Zero(self):
        self.log.debug("Axis0_SetAngle2Zero")
        return self.ResetPos(0)

    def Axis1_SetAngle2Zero(self):
        self.log.debug("Axis1_SetAngle2Zero")
        return self.ResetPos(1)

    def Axis0_GetMaxSpeed(self):  
        reg = self.GetParam(0, "MAX_SPEED")

        ret = 15.2588 * float(reg) * self.DEGS_PER_STEP_0 # step / s * deg / step

        self.log.debug("Axis0_GetMaxSpeed %f degs/s", ret)
        return ret

    def Axis1_GetMaxSpeed(self): # steps / s
        reg = self.GetParam(1, "MAX_SPEED")
        ret = 15.2588 * float(reg) * self.DEGS_PER_STEP_1 

        self.log.debug("Axis1_GetMaxSpeed %f degs/s", ret)
        return ret
 
###############################################
# Testing
import logging

def main():
    print("Class Motors")
    print("Runtests ...")
    
    m = STWMotorsLowLevel(logging.getLogger())

    m.Init()

    if not m.isInitialized:
        return
    
    m.SoftStop(0)
    m.SoftStop(1)

    max_speed_0 = m.Axis0_GetMaxSpeed()
    print(max_speed_0)
    
    max_speed_1 = m.Axis1_GetMaxSpeed()
    print(max_speed_1)

    m.Axis0_SetAngle(0)    
    print(m.Axis0_Angle())    
    t = time.time()
    m.Axis0_SlewTo(1)
    m.WaitIsBusy(0)
    print("Axis 0 " + str(time.time() - t) + "s")

    m.Axis1_SetAngle(0)
    print(m.Axis1_Angle())
    t = time.time()
    m.Axis1_SlewTo(1)
    m.WaitIsBusy(1)
    print("Axis 1 " + str(time.time() - t) + "s")

    m.Axis0_SlewTo(1)
    m.Axis1_SlewTo(1)

    m.WaitIsBusy(0)
    m.WaitIsBusy(1)

    print(m.Axis0_Angle())
    print(m.Axis1_Angle())

 #   m.Axis0_SlewTo(359)
 #   m.Axis1_SlewTo(-2)

 #   m.WaitIsBusy(0)
 #   m.WaitIsBusy(1)

 #   print(m.Axis0_Angle())
 #   print(m.Axis1_Angle())

 #   m.Axis0_SlewTo(0)
 #   m.Axis1_SlewTo(0)

 #   m.WaitIsBusy(0)
 #   m.WaitIsBusy(1)

 #   print(m.Axis0_Angle())
 #   print(m.Axis1_Angle())

    print(m.GetStatusErrorBitsMsg(0))
    print(m.GetStatusErrorBitsMsg(1))

import time

if __name__ == "__main__":
    main()