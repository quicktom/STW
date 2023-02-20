
"""
    Protocol layer over serial port to the X-CUBE-SPN2 board and firmware.

    Stepper level.

    "off chip registers" needs  firmare_tweaked_v0.3 or higher.
"""


"""
    16.08.2022
    - erstes Motoren Setup
    - BEMF ausgeschaltet
    - Übersetzung und Geschwindigkeit von Motor 0 passt

    Motor 1
    - TODO Übersetzung von Motor 1 1:83.333 testen
    - TODO OCD_TH, STALL_TH erhöhen -> höhere KVALS und Geschwindigkeit testen

    Drehrichtung anpassen
    - TODO Drehung von Ost nach West ist "negativ" testen 
    - TODO Drehung von Äquator zum Pol ist "positiv" testen

    Tracking
    - TODO Geschwindigkeit testen  

    17.08.2022
    - Übersetzung von Motor 1 ist 1:83.333 OK
    - nach Tuning Kx und MAX_SPEED Motor 0 0.23deg/s und Motor 1 0.38deg/s
    Motor 0 {"ACC": 10, "DEC": 10, "MAX_SPEED": 72, "MIN_SPEED": 0, "KVAL_HOLD": 0, "KVAL_RUN": 30, "KVAL_ACC": 30, "KVAL_DEC": 30, "INT_SPEED": 1, "ST_SLP": 0, "FN_SLP_ACC": 0, "FN_SLP_DEC": 0, "K_THERM": 0, "OCD_TH": 10, "STALL_TH": 111, "FS_SPD": 0, "STEP_MODE": 0, "ALARM_EN": 255, "CONFIG": 11912}
    Motor 1 {"ACC": 27, "DEC": 27, "MAX_SPEED": 122, "MIN_SPEED": 0, "KVAL_HOLD": 0, "KVAL_RUN": 42, "KVAL_ACC": 42, "KVAL_DEC": 42, "INT_SPEED": 1, "ST_SLP": 0, "FN_SLP_ACC": 0, "FN_SLP_DEC": 0, "K_THERM": 0, "OCD_TH": 5, "STALL_TH": 65, "FS_SPD": 0, "STEP_MODE": 0, "ALARM_EN": 255, "CONFIG": 11912}
    - TODO verschiedene Lagen testen ggf. ist das notwendige Drehmoment nicht konstant
    - Drehung von Ost nach West ist positiv TODO Verdrahtung ändern? Oder ?
    - Drehung von Äquator zum Pol ist negativ TODO Verdrahtung ändern? Oder ?
    - Tracking Motor 0 hackt -> TODO Absenkung der KVAL_x für kleine Geschwindigkeiten KVAL_x auf 12 bei SPEED 19
    - TODO BEMF Einstellung mit dem STM- Tool testen

    18.08.2022
    - BEMF Motor 0 {"ACC": 10, "DEC": 10, "MAX_SPEED": 75, "MIN_SPEED": 0, "KVAL_HOLD": 0, "KVAL_RUN": 12, "KVAL_ACC": 12, "KVAL_DEC": 12, "INT_SPEED": 2304, "ST_SLP": 1, "FN_SLP_ACC": 6, "FN_SLP_DEC": 6, "K_THERM": 0, "OCD_TH": 10, "STALL_TH": 111, "FS_SPD": 0, "STEP_MODE": 0, "ALARM_EN": 255, "CONFIG": 11912}
      läuft ohne "Rattern" bei hoher MAX_SPEED (mechanische Begrenzung des Planentengetriebes?) und ohne "Hacken" bei SolarSpeed
    - TODO StepClockMode für SolarSpeed für bessere Anpassung prüfen
    - Drehmoment für ein paar Lagen getestet OK
    - Verdrahtung Motor 0 getauscht Ost->West ist negativ OK
    - Verdrahtung Motor 1 getauscht Äquator zu Pol ist positiv wenn Linksauslage OK
    - ACHTUNG: Bei "Rechtssauslage" ist jetzt Äquator zu Pol ist negativ
    
    24.08.2022
    - TODO StepClockMode für SolarSpeed

    27.08.2022
    - TODO StepClockMode auf (D8) PA9 als TIM1_CH2 als PWM

    29.08.2022
    - new firmware off chip register REGEX0 as PWM control

    30.08.2022
    - TODO StepClockMode: Pin PA9 TIM1_CH2 connect J3  / Pin PC7 TIM3_CH2 connect to J4 

"""

import STWobject
import serial, string
import json 

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
    def Init(self, loadConfigFromFile = True, M0RegisterConfig = 'M0.json', M1RegisterConfig = 'M1.json', comPort = 'COM6'):
        
        self.log.info("Initialize board.")

        try:
            self.serialPort = serial.Serial(comPort, 115200, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, 0.01, True)
        except:
            self.log.fatal("Unable to open serial port.")
            self.isInitialized = False
            return

        # upper level must check and quit
        self.isInitialized = True

        if loadConfigFromFile:
            self.log.info("Load motor config from file.")
            self.LoadConfigRegistersFromFile(0, M0RegisterConfig)
            self.LoadConfigRegistersFromFile(1, M1RegisterConfig)
        else:
            self.log.info("Use motor config from firmware.")
        
        self.log.info("Motors initialized.")

    def Shutdown(self):
        if self.isInitialized:
            self.serialPort.close() 
 
    #Send and Receive from motordriver
    def __SendReceiveCmd(self, motorId, sendToMotorStr, receiveFromMotor = False, checkRetValue = True):
        if(self.isInitialized):   
            cmd = "M"+ str(motorId) + "." + sendToMotorStr + '\r'
            # send command to X-CUBE-SPN2
            self.serialPort.write(bytes(cmd,'utf-8'))
            # receive answer from X-CUBE-SPN2
            ret = self.serialPort.readline().decode("utf-8")[:-2]

            # Check answers to detect errors
            if checkRetValue:
                # ret is "ERROR"
                # malformed cmd sent
                if ret == "ERROR":
                    self.log.error("Error <%s>.", cmd)
                    if receiveFromMotor:
                        return False, -1
                    else:
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
        status, answer = self.__SendReceiveCmd(motorId, "GETPARAM."  + paramStr, True)
        return answer

    # higher level functions
    def Run(self, motorId, dir, speed):
        status = self.__SendReceiveCmd(motorId, "RUN."  + dir + "." + str(speed))
        return status

    def Move(self, motorId, dir, steps):
        status = self.__SendReceiveCmd(motorId, "MOVE."  + dir + "." + str(steps))
        return status

    def StepClockMode(self, motorId, dir):
        status = self.__SendReceiveCmd(motorId, "STEPCLOCK."  + dir)
        return status

    def GotoDir(self, motorId, dir, abs_pos):
        status = self.__SendReceiveCmd(motorId, "GOTO_DIR." + dir + "." + str(abs_pos))

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
    
    #Configure 
    def GetRegs(self, motorId, dict):
        return {x: self.GetParam(motorId, x) for x in dict }

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
            else:
                return int(self.L6470_POSITION_RANGE + 1)        
    
    # from register to value
    def AbsPos2Pos(self, abspos):
        if (abspos > self.L6470_MAX_POSITION):
            return abspos - (self.L6470_POSITION_RANGE + 1)
        else:
            return abspos

    def StepsHz2SpeedReg(self, StepsHz):
        if StepsHz <= (self.L6470_MAX_SPEED * (self.L6470_SPEEDREG_2_STEPSHZ)):
            return int(float(StepsHz) / (self.L6470_SPEEDREG_2_STEPSHZ))
        else:
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

        self.SoftStop(motorId)
                
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
    m.GotoPosCmdDir(0, 1000)
    m.WaitIsBusy(0)
    print(m.GetPosCmd(0))
    m.GotoPosCmdDir(0, -1000)
    m.WaitIsBusy(0)
    print(m.GetPosCmd(0))
    m.GotoPosCmdDir(0, 1000)
    m.WaitIsBusy(0)
    print(m.GetPosCmd(0))
    m.GotoPosCmdDir(0, 0)
    m.WaitIsBusy(0)
    print(m.GetPosCmd(0))

if __name__ == "__main__":
    main()