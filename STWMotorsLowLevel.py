#!/usr/bin/python3

"""
    Protocol layer to the module STWMicroController.

    Angle level.

    Implement low level function of motor movement.
"""

import STWMicroController
import MountSpecs

class STWMotorsLowLevel(STWMicroController.board):

    def StepsPerAngle(self, motorId, angle):
        if motorId == 0:
            return  angle*(MountSpecs.RAStepsPerRevolution*self.GetMircoSteps(0)/360) 
        else:
            return  angle*(MountSpecs.DEStepsPerRevolution*self.GetMircoSteps(1)/360) 

    def AnglePerSteps(self, motorId, steps):
        if motorId == 0:
            return  360.0*steps/(MountSpecs.RAStepsPerRevolution*self.GetMircoSteps(0))
        else:
            return  360.0*steps/(MountSpecs.DEStepsPerRevolution*self.GetMircoSteps(1)) 
        
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
        return self.RunCmd(0, self.StepsPerAngle(0, angle_per_s)/self.GetMircoSteps(0))

    def Axis1_Run(self, angle_per_s):
        return self.RunCmd(1, self.StepsPerAngle(1, angle_per_s)/self.GetMircoSteps(0))

    def Axis0_Angle(self):
        return self.AnglePerSteps(0, self.GetPosCmd(0))

    def Axis1_Angle(self):
        return self.AnglePerSteps(1, self.GetPosCmd(1))

    def Axis0_SetAngle(self, angle):
        return self.SetPosCmd(0, self.StepsPerAngle(0, angle))

    def Axis1_SetAngle(self, angle):
        return self.SetPosCmd(1, self.StepsPerAngle(1, angle))
        
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
        ret = self.AnglePerSteps(0, 15.2588 * float(reg)*self.GetMircoSteps(0))
        self.log.debug("Axis0_GetMaxSpeed %f degs/s", ret)
        return ret

    def Axis1_GetMaxSpeed(self): 
        reg = self.GetParam(1, "MAX_SPEED")
        ret = self.AnglePerSteps(1, 15.2588 * float(reg)*self.GetMircoSteps(1))
        self.log.debug("Axis1_GetMaxSpeed %f degs/s", ret)
        return ret
 
###############################################
# Testing
import logging, time

def main():
    print("Class Motors")
    print("Runtests ...")
    
    m = STWMotorsLowLevel(logging.getLogger())

    m.Init()

    if not m.isInitialized:
        return
    
    print(m.GetStatusErrorBitsMsg(0))
      
    m.SoftStop(0)
    m.WaitIsBusy(0)

    max_speed_0 = m.Axis0_GetMaxSpeed()
    print(max_speed_0)

    # m.Axis0_Run(-360/86400)
    # time.sleep(30)
    # m.Axis0_SoftStop()
    # m.WaitIsBusy(0)

    # m.Axis0_SetAngle(0)
    # print(m.GetStatusErrorBitsMsg(0))
    # for i in range(10):
    #     print(m.Axis0_Angle())    
    #     m.Axis0_SlewTo(1/120)
    #     m.WaitIsBusy(0)
    #     print(m.GetStatusErrorBitsMsg(0))
    #     print(m.Axis0_Angle())
    #     time.sleep(1)

    #     m.Axis0_SlewTo(-1/120)
    #     m.WaitIsBusy(0)
    #     print(m.GetStatusErrorBitsMsg(0))
    #     print(m.Axis0_Angle())
    #     time.sleep(1)

    m.Axis0_SetAngle(0)

    for i in range(1):
        print(m.Axis0_Angle())
        m.Axis0_SlewTo(1)
        m.WaitIsBusy(0)
        print(m.Axis0_Angle())
        m.Axis0_SlewTo(-1)
        m.WaitIsBusy(0)
        print(m.Axis0_Angle()) 
        m.Axis0_SlewTo(0)
        m.WaitIsBusy(0)
        print(m.Axis0_Angle()) 
import time

if __name__ == "__main__":
    main()