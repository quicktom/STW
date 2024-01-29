
"""
    Protocol layer over serial port to the X-CUBE-SPN2 board and firmware.

    Stepper level.

    "off chip registers" needs  firmare_tweaked_v0.3 or higher.
"""

import json
import string, serial
import STWobject
import MountSpecs

class board(STWobject.stwObject):

        # Common register definition
    StatusRegs = {  'ABS_POS'   : 0,    # Current position
                    'EL_POS'    : 0,    # Electrical position
                    'MARK'      : 0,    # Mark position
                    'SPEED'     : 0,    # Current speed
                    'STATUS'    : 0,    # Status (the reset value is according to startup conditions)
                    'ADC_OUT'   : 0,    # ADC output (the reset value is according to startup conditions)
                }

    ConfigRegs = {  'ACC'       : 0,    # Acceleration
                    'DEC'       : 0,    # Deceleration
                    'MAX_SPEED' : 0,    # Maximum speed
                    'MIN_SPEED' : 0,    # Minimum speed
                    'KVAL_HOLD' : 0,    # Holding KVAL
                    'KVAL_RUN'  : 0,    # Constant speed KVAL
                    'KVAL_ACC'  : 0,    # Acceleration starting KVAL
                    'KVAL_DEC'  : 0,    # Deceleration starting KVAL
                    'INT_SPEED' : 0,    # Intersect speed
                    'ST_SLP'    : 0,    # Start slope
                    'FN_SLP_ACC': 0,    # Acceleration final slope
                    'FN_SLP_DEC': 0,    # Deceleration final slope
                    'K_THERM'   : 0,    # Thermal compensation factor
                    'OCD_TH'    : 0,    # OCD threshold
                    'STALL_TH'  : 0,    # STALL threshold
                    'FS_SPD'    : 0,    # Full-step speed
                    'STEP_MODE' : 0,    # Step mode
                    'ALARM_EN'  : 0,    # Alarm enable
                    'CONFIG'    : 0,    # IC configuration
                }
         
    #Open motordriver comport
    def Init(self, loadConfigFromFile = True, M0RegisterConfig = MountSpecs.RAMotorConfigFile, M1RegisterConfig = MountSpecs.DEMotorConfigFile, comPort = 'COM4'):
        
        self.log.info("Initialize board.")

        try:
            self.serialPort = serial.Serial(comPort, 921600, serial.EIGHTBITS, serial.PARITY_NONE,\
                                             serial.STOPBITS_ONE, xonxoff = True, rtscts = False, dsrdtr = False)
        except:
            self.log.fatal("Unable to open serial port.")
            self.log.fatal("Hard quit program.")
            self.isInitialized = False
            print("Press Enter to continue ...")
            input() 
            # 
            quit()
            
        # upper level must check and quit
        self.isInitialized = True

        # reset serial buffers
        self.serialPort.reset_output_buffer()
        self.serialPort.reset_input_buffer()

        # check com protocol
        # try GETSTATUS from motor driver 0,1
        # on reponse it is good
        status, _ = self.__SendReceiveCmd(0, "GETSTATUS", True)
        if not status:
            self.log.fatal("Motor driver 0 does not respond.")
            quit()
  
        status, _ = self.__SendReceiveCmd(1, "GETSTATUS", True)
        if not status:
            self.log.fatal("Motor driver 1 does not respond.")
            quit()

        # load motor config 
        if loadConfigFromFile:
            self.log.info("Load motor config from file.")
            self.LoadConfigRegistersFromFile(0, M0RegisterConfig)
            self.LoadConfigRegistersFromFile(1, M1RegisterConfig)
        else:
            self.log.info("Use motor config from firmware.")
        
        

        self.log.info("Motors initialized.")

    def Shutdown(self):
        if self.isInitialized:
            # reset serial buffers
            self.serialPort.reset_output_buffer()
            self.serialPort.reset_input_buffer()
            self.serialPort.close() 
 
    #Send and Receive from motordriver
    def __SendReceiveCmd(self, motorId, sendToMotorStr, receiveFromMotor = False, checkRetValue = True):
        if self.isInitialized:   
            cmd = "M"+ str(motorId) + "." + sendToMotorStr + '\r'
            # send command to X-CUBE-SPN2
            self.serialPort.write(bytes(cmd,'utf-8'))
            # receive answer from X-CUBE-SPN2
            ret = self.serialPort.readline().decode("utf-8")[:-2]

            # Check answers to detect errors
            if checkRetValue:
                # check empty return value
                if receiveFromMotor and not ret:
                    self.log.error("Empty return value <%s>.", cmd)
                    return False, -1 

                # ret is "ERROR"
                # malformed cmd sent
                if ret == "ERROR":
                    self.log.error("Error <%s>.", cmd[:-1])
                    if receiveFromMotor:
                        return False, -1
                    
                    return False

                # ret malformed hexnumber or empty ret
                if receiveFromMotor and not all(c in string.hexdigits for c in ret):
                    self.log.error("Result error <%s>.", cmd)
                    return False, -1

            if receiveFromMotor:
                return True, int(ret,16)
            else:       
                return True        
        else:
            self.log.error("Error board not initialized.")
            return False

    def SetParam(self, motorId, paramStr, value):
        status = self.__SendReceiveCmd(motorId, "SETPARAM."  + paramStr + "." + str(value))
        return status

    def GetParam(self, motorId, paramStr):
        __, answer = self.__SendReceiveCmd(motorId, "GETPARAM."  + paramStr, True)
        return answer

    # higher level functions
    def Run(self, motorId, direction, speed):
        status = self.__SendReceiveCmd(motorId, "RUN."  + direction + "." + str(speed))
        return status

    def Move(self, motorId, direction, steps):
        status = self.__SendReceiveCmd(motorId, "MOVE."  + direction + "." + str(steps))
        return status

    def StepClockMode(self, motorId, direction):
        status = self.__SendReceiveCmd(motorId, "STEPCLOCK."  + direction)
        return status

    def GotoDir(self, motorId, direction, abs_pos):
        status = self.__SendReceiveCmd(motorId, "GOTO_DIR." + direction + "." + str(abs_pos))
        return status
    
    def Goto(self, motorId, abs_pos):
        status = self.__SendReceiveCmd(motorId, "GOTO."  + str(abs_pos))
        return status

    def GetStatus(self, motorId):
        status, answer = self.__SendReceiveCmd(motorId, "GETSTATUS", True)
        return answer

    def ResetPos(self, motorId):
        status = self.__SendReceiveCmd(motorId, "RESETPOS")
        return status

    def ResetDevice(self, motorId):
        status = self.__SendReceiveCmd(motorId, "RESETDEVICE")
        return status

    def SoftStop(self, motorId):
        status = self.__SendReceiveCmd(motorId, "SOFTSTOP")
        return status

    def HardStop(self, motorId):
        status = self.__SendReceiveCmd(motorId, "HARDSTOP")
        return status

    def SoftHiZ(self, motorId):
        status = self.__SendReceiveCmd(motorId, "SOFTHIZ")
        return status

    def HardHiZ(self, motorId):
        status = self.__SendReceiveCmd(motorId, "HARDHIZ")
        return status
    
    def NopCmd(self, motorId):
        status = self.__SendReceiveCmd(motorId, "NOP")
        return status
    
    #Configure 
    def GetRegs(self, motorId, regdict):
        return {x: self.GetParam(motorId, x) for x in regdict }

    def SetRegs(self, motorId, data):
        return {x: self.SetParam(motorId, x, data[x]) for x in data }

    def PrintConfigRegs(self, motorId):
        r = self.GetRegs(motorId, self.ConfigRegs)
        
        for x in self.ConfigRegs:
            print(x + '\t :' + hex(r[x]))

        return True

    def LoadConfigRegistersFromFile(self, motorId, fname):
        
        self.SoftStop(motorId)
        self.SoftHiZ(motorId)

        with open(fname, 'r') as fp:
            data = json.load(fp)
            fp.close()
        
        self.SetRegs(motorId, data)

        # verify register file written 
        regs = self.GetRegs(motorId, self.ConfigRegs)
        for x in self.ConfigRegs:
            if regs[x] != data[x]:
                self.log.fatal("Could not verify register file. (failed at " + x + ")")
                quit()

        # L6470 datasheet p. 64
        # When the motor is in high impedance state, a SoftStop command forces the bridges to exit
        # from high impedance state; no motion is performed.
        self.SoftStop(motorId)
        self.ResetPos(motorId)

    def SaveConfigRegistersToFile(self, motorId, fname):

        r = self.GetRegs(motorId, self.ConfigRegs)
        with open(fname, 'wt') as fp:
            json.dump(r,fp)
            fp.close()

        return True
    
    #
    #   driver helpers
    #
    # L6470 constants
    #      
    L6470_MAX_POSITION          = 0x1FFFFF
    L6470_MIN_POSITION          = (-(0x200000)) 
    L6470_POSITION_RANGE        = L6470_MAX_POSITION - L6470_MIN_POSITION
    L6470_MAX_SPEED             = 0xFFFFF
    L6470_SPEEDREG_2_STEPSHZ    = 0.014901161193848

    #Conversion
    # from value to register
    def Pos2AbsPos(self, position):
        if (position >= 0) & (position < self.L6470_MAX_POSITION):
            return int(position)
        else:
            if (position >= self.L6470_MIN_POSITION) & (position < 0):
                return int(position + (self.L6470_POSITION_RANGE + 1))
            
            return int(self.L6470_POSITION_RANGE + 1)        
    
    # from register to value
    def AbsPos2Pos(self, abspos):
        if (abspos > self.L6470_MAX_POSITION):
            return abspos - (self.L6470_POSITION_RANGE + 1)
        
        return abspos

    def StepsHz2SpeedReg(self, StepsHz):
        if StepsHz <= (self.L6470_MAX_SPEED * (self.L6470_SPEEDREG_2_STEPSHZ)):
            return int(float(StepsHz) / (self.L6470_SPEEDREG_2_STEPSHZ))
        
        return 0 # warning  

    def SpeedReg2StepsHz(self, reg):
        return reg * self.L6470_SPEEDREG_2_STEPSHZ

    #
    # high level driver
    #

    def isHiZ(self, status):
        return bool(status & 0b0001)

    def isBUSY(self, status):
        return bool(not(status & (0b0001 << 1)))
    
    def isDIR(self, status):
        return bool(status & (0b0001 << 4))

    def isMotorStopped(self, status):
        return ((status >> 5) & 0b0011) == 0

    def isMotorAcceleration(self, status):
        return ((status >> 5) & 0b0011) == 1

    def isMotorDeceleration(self, status):
        return ((status >> 5) & 0b0011) == 2

    def isMotorConstantSpeed(self, status):
        return ((status >> 5) & 0b0011) == 3

    def isNotPerformedCmd(self, status):
        return bool(status & (0b0001 << 7))

    def isWrongCmd(self, status):
        return bool(status & (0b0001 << 8))

    def isUVLO(self, status):
        return bool(not(status & (0b0001 << 9)))

    def isThermalWarning(self, status):
        return bool(not (status & (0b0001 << 10)))

    def isThermalShutDown(self, status):
        return bool(not (status & (0b0001 << 11)))

    def isOCD(self, status):
        return bool(not (status & (0b0001 << 12)))

    def isStepLossA(self, status):
        return bool(not (status & (0b0001 << 13)))

    def isStepLossB(self, status):
        return bool(not (status & (0b0001 << 14)))

    StatusBitsPtr = [isHiZ, isBUSY, isDIR, isMotorStopped, isNotPerformedCmd, isWrongCmd, isUVLO,  \
        isThermalWarning, isThermalShutDown, isOCD, isStepLossA, isStepLossB, isMotorAcceleration, \
            isMotorDeceleration, isMotorConstantSpeed]
    StatusBitsStr = ["HiZ", "BUSY", "DIR", "MotorStopped", "NotPerformedCmd", "WrongCmd", "UVLO",  \
        "ThermalWarning", "ThermalShutDown", "OCD", "StepLossA", "StepLossB", "MotorAcceleration", \
            "MotorDeceleration", "MotorConstantSpeed"]

    def GetStatusBitsMsg(self, motorId):
        status = self.GetStatus(motorId)
        return {self.StatusBitsStr[i]: self.StatusBitsPtr[i](self, status) for i in range(0,len(self.StatusBitsPtr))} 

    StatusErrorBitsPtr = [ isNotPerformedCmd, isWrongCmd, isUVLO,  \
        isThermalWarning, isThermalShutDown, isOCD, isStepLossA, isStepLossB]
    StatusErrorBitsStr = ["NotPerformedCmd", "WrongCmd", "UVLO",  \
        "ThermalWarning", "ThermalShutDown", "OCD", "StepLossA", "StepLossB"]

    def GetStatusErrorBitsMsg(self, motorId):
        status = self.GetStatus(motorId)
        return {self.StatusErrorBitsStr[i]: self.StatusErrorBitsPtr[i](self, status) for i in range(0,len(self.StatusErrorBitsPtr))} 

    def GetErrorStatus(self, motorId):
        status = self.GetStatus(motorId)
        ret = {}

        for i in range(0,len(self.StatusErrorBitsPtr)):
            if(self.StatusErrorBitsPtr[i](self, status)):
                self.log.fatal("Motor driver <%i> reports an error status bit <%s>", motorId, self.StatusErrorBitsStr[i])
                ret[self.StatusErrorBitsStr[i]] = True

        return ret

    # high level signed goto commands
    def GotoPosCmd(self, motorId, position):
        return self.Goto(motorId, self.Pos2AbsPos(position))

    def GotoPosCmdDir(self, motorId, position):
        if  position > self.GetPosCmd(motorId):
            self.GotoDir(motorId, "FWD", self.Pos2AbsPos(position))
        else:
            self.GotoDir(motorId, "REV", self.Pos2AbsPos(position))

    def GetPosCmd(self, motorId):
        return self.AbsPos2Pos(self.GetParam(motorId, 'ABS_POS'))

    def SetPosCmd(self, motorId, position):
        return self.SetParam(motorId, "ABS_POS", self.Pos2AbsPos(position))

    def RunCmd(self, motorId, StepsHz):
        if StepsHz >= 0:
            DirStr = 'FWD'
        else:
            DirStr = 'REV'
            StepsHz = -StepsHz
    
        return self.Run(motorId, DirStr, self.StepsHz2SpeedReg(StepsHz))

    def MoveCmd(self, motorId, Steps):
        if Steps >= 0:
            DirStr = 'FWD'
        else:
            DirStr = 'REV'
            Steps = -Steps     
    
        return self.Move(motorId, DirStr, int(Steps))

    def IsBusy(self, motorId):
        return self.isBUSY(self.GetStatus(motorId))

    def WaitIsBusy(self, motorId):
        while(self.IsBusy(motorId)):
            pass

    def WaitSoftStop(self, motorId):
        self.log.debug("WaitSoftStop.")                
        self.WaitIsBusy(motorId)
        
        return True

    """ firmware specific """
    """ off chip registers for StepClockMode """
    """ StepClockMode for high resolution frequency stepping """
    def SetRegEx0(self, motorid, value):
        return self.__SendReceiveCmd(motorid,"REGEX0." + str(value), receiveFromMotor=True)

    """ StepClockMode """
    def StepClockModeOn(self, motorId, stepsHz):
        self.logger.info("StepClockModeOn not implemented.")    

        """ Any attempt to perform a StepClock command when the motor is running causes the
            command to be ignored and the NOTPERF_CMD flag. page 60 - force and wait for no movement """
        self.WaitSoftStop(motorId)

        if stepsHz >= 0:
            self.StepClockMode(motorId, "FWD")
        else:
            self.StepClockMode(motorId, "REV")

        "start pwm generation"
        "TODO conversion to register not implemented"
        return self.SetRegEx0(self, motorId, stepsHz)

    def StepClockModeOff(self, motorId): 
        """ The device exits from Step-clock mode when a constant speed, absolute positioning or
            motion command is sent through SPI, page 60 - nothing to do about it """      

        "stop pwm generation"
        " 0 stops pwm generation "
        return self.SetRegEx0(motorId, 0)


###############################################
# Testing
import logging

def main():
    print("Class board")
    print("Runtests ...")
    
    m = board(logging.getLogger())

    m.Init(loadConfigFromFile=True)

    if not m.isInitialized:
        print("Board not initialized.")
        return

    print(m.GetErrorStatus(0))
    print(m.GetErrorStatus(1))


    m.SetPosCmd(0,0)
    print(m.GetPosCmd(0))
    m.GotoPosCmdDir(0, 10000)
    m.WaitIsBusy(0)
    print(m.GetPosCmd(0))
    print(m.GetErrorStatus(0))
    
 #   m.GotoPosCmdDir(0, -1000)
 #   m.WaitIsBusy(0)
 #   print(m.GetPosCmd(0))
 #   m.GotoPosCmdDir(0, 1000)
 #   m.WaitIsBusy(0)
 #   print(m.GetPosCmd(0))
 #   m.GotoPosCmdDir(0, 0)
 #   m.WaitIsBusy(0)
 #   print(m.GetPosCmd(0))

if __name__ == "__main__":
    main()