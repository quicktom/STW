# -*- coding: utf-8 -*-
""" STWcomponents module of the observator project.

This module abstracts stellarium functions.

Todo:

"""

import STWobject, STWsystem, STWastrometry, STWusercontrol, STWstellarium, STWJob, STWMotors

import json

from signal import signal, SIGINT

from  tictoc import Timer

class components(STWobject.stwObject):
    def __init__(self, logger, Aligned2WestPier, comportDevStr):
        super().__init__(logger)

        # abstract system functions
        self.sys        = STWsystem.sys(self.log)
        
        # abstract astrometry functions
        self.astroguide = STWastrometry.astroguide(self.log, Aligned2WestPier)

        # abstract user input functions
        self.uc         = STWusercontrol.uc(self.log)

        # abstract stellarium functions
        self.stellarium = STWstellarium.stellarium(self.log)
        
        # abstract telescope mount functions
        self.mount      = STWMotors.mount(self.log, comportDevStr)
        
        # ntp time offset
        self.TimeOffsetSec = 0
        
        # slewing speed is a fraction of maxspeed
        self.SlewSpeedFactor   = 0.1  

        # mount is tracking
        self.IsMountTracking = False

        # actual action
        self.ActualActionStr = "Start up"

# start basic initialisation phase
    def Init(self):
        self.log.info("Start basic initialisation phase.")

        self.sys.Init()
        self.astroguide.Init()
        self.stellarium.Init()
        self.uc.Init()
        self.mount.Init()

        # CTRL-C detection to exit self.Loop
        signal(SIGINT, self.handlerSIGINT)
        self.ControlCDetected = False
        self.log.info("Press CTRL-C to leave loop.")

    def handlerSIGINT(self, signal_received, frame):
        self.log.info("SIGINT or CTRL-C detected.")
        self.ControlCDetected = True

    def Config(self):
        self.log.info("Start configuration phase.")

        self.astroguide.Config()
        self.uc.Config()
        self.sys.Config()
        self.stellarium.Config()
        self.mount.Config()

        # try to get time offset to system time via NTP
        ret = self.sys.GetNtpOffsetSec()
        if ret[0]:
            self.TimeOffsetSec = ret[1]
            self.log.info("Time offset to NTP Server is %3.2fs", self.TimeOffsetSec)
        else:   
            self.log.info("Unable to detect time offset to NTP Server")

        return super().Config()

    def PreLoop(self):
        self.log.info("Start preloop phase.")

    def ExitLoop(self):
        self.log.info("Start exit loop phase.")

    def Shutdown(self):
        self.log.info("Start shutdown phase.")
        
        self.astroguide.Shutdown()
        self.uc.Shutdown()
        self.sys.Shutdown()
        self.stellarium.Shutdown()
        self.mount.Shutdown()

    def DoDataLog(self, CurrentEt):
        self.log.debug("Log current telescope state.")
        try:
            datafile = open("datadata.json", 'r+')
            file_data = json.load(datafile)
        except FileNotFoundError:
            # if not existe create new and start over
            datafile =  open("datadata.json",'w+')
            file_data = {}
            file_data["data"] = []                       
        finally:
            # update 
            self.astroguide.SetActual(CurrentEt, self.mount.Axis0_Angle(), self.mount.Axis1_Angle())
      
            state = {   "et":               CurrentEt,
                        "UTC":              self.astroguide.GetUTCTimeStrFromEt(CurrentEt),    
                        "TelescopeLon":     self.astroguide.Actual.lon,  
                        "TelescopeLat":     self.astroguide.Actual.lat,
                        "TargetLon":        self.astroguide.Target.lon,
                        "TargetLat":        self.astroguide.Target.lat,
                        "TargetRa":         self.astroguide.Target.ra,
                        "TargetDe":         self.astroguide.Target.de,
                        "IsWestPier":       self.astroguide.Aligned2WestPier }
            
            file_data["data"].append(state)
            # overwrite file contents
            datafile.truncate(0)
            datafile.seek(0)

            json.dump(file_data, datafile, indent = 4)
            datafile.close()

    def DoUserControlJob(self, CurrentEt):
        # get user inputs
        remote = self.uc.listen()
        if remote:
                #           C   is speed up
                #           D   is speed down
                #           Y(+UDC)   is telescope lat
                #           X(+LRC)   is telescope lon
                #           B   is tracking on/off is stop mount
                #           S1  is slew telescope to stellarium target
                #           S2  is sync telescope coords to stellarium reference
                #           A   is log current state 

            match remote:

                case 'S1':
                    self.log.debug("Slew telescope to target.")
                    self.mount.Axis0_SlewTo(self.astroguide.Target.lon)
                    self.mount.Axis1_SlewTo(self.astroguide.Target.lat)
                    self.ActualActionStr = "Slew to target."
                    self.IsMountTracking = False

                case 'S2':
                    self.log.debug("Set telescope reference.")
                    self.mount.SoftStopMotors(wait= True)
                    self.mount.Axis0_SetAngle(self.astroguide.Target.lon)
                    self.mount.Axis1_SetAngle(self.astroguide.Target.lat)
                    self.ActualActionStr = "Got reference point."

                case 'XC':
                    self.mount.Axis0_SoftStop()
                    self.ActualActionStr = "Stopping."

                case 'XR':
                    self.IsMountTracking = False
                    self.mount.SlewConstantSpeed(0, self.SlewSpeedFactor, self.mount.Axis0_GetMaxSpeed(), 1)
                    self.ActualActionStr = "Move."

                case 'XL':
                    self.IsMountTracking = False
                    self.mount.SlewConstantSpeed(0, self.SlewSpeedFactor, self.mount.Axis0_GetMaxSpeed(), -1)
                    self.ActualActionStr = "Move."
                
                case 'YC':
                    self.mount.Axis1_SoftStop()
                    self.ActualActionStr = "Stopping."

                case 'YU':
                    self.IsMountTracking = False
                    # slew with slow axis speed
                    self.mount.SlewConstantSpeed(1, self.SlewSpeedFactor, self.mount.Axis0_GetMaxSpeed(), 1)
                    self.ActualActionStr = "Move."

                case 'YD':
                    self.IsMountTracking = False
                    # slew with slow axis speed
                    self.mount.SlewConstantSpeed(1, self.SlewSpeedFactor, self.mount.Axis0_GetMaxSpeed(), -1)
                    self.ActualActionStr = "Move."

                case 'B':
                    if(self.IsMountTracking):
                        self.log.debug("Stop constant speed tracking")
                        self.IsMountTracking = False
                        self.mount.SoftStopMotors()
                        self.ActualActionStr = "Stopping."
                    else:
                        self.log.debug("Start constant speed tracking")
                        self.IsMountTracking = True
                        self.mount.SoftStopMotors()
                        self.mount.SetConstantSpeed(self.lonps, self.latps)
                        self.ActualActionStr = "Tracking."

                case 'D':
                    if self.SlewSpeedFactor > 0.1:
                        self.SlewSpeedFactor = self.SlewSpeedFactor - 0.1
                    else:
                        self.SlewSpeedFactor = 0.1

                    self.log.debug("Set SlewSpeedFactor to %f", self.SlewSpeedFactor)
                
                case 'C':
                    if self.SlewSpeedFactor < 0.9:
                        self.SlewSpeedFactor = self.SlewSpeedFactor + 0.1
                    else:
                        self.SlewSpeedFactor = 0.9

                    self.log.debug("Set SlewSpeedFactor to %f", self.SlewSpeedFactor)

                case 'A':
                    self.DoDataLog(CurrentEt)
                    
                case _: self.log.error("Undefinded user control command %s received.", remote)

            

    def DoStellariumInput(self, CurrentEt):
        ret, ra, de  = self.stellarium.ReceiveFromStellarium()
        if ret:
            self.astroguide.SetTarget(CurrentEt, ra, de)
    
    def DoStellariumOutput(self):
        # Simulation reflects target lon, lat
        self.stellarium.SendToStellarium(self.astroguide.Actual.ra, self.astroguide.Actual.de)

    # main loop, non blocking
    def Loop(self):
        self.log.info("Start loop phase.")

        CurrentEt = self.astroguide.GetSecPastJ2000TDBNow(offset = self.TimeOffsetSec)

        # periodic process inputs and outputs 
        loopPeriodic = STWJob.STWJob(0.5)           # 0.5 secs
        loopPeriodic.startJob(CurrentEt)

        # update to stellarium
        stellariumPeriodicSend = STWJob.STWJob(0.5) # 0.5 secs 
        stellariumPeriodicSend.startJob(CurrentEt)

        # print stattistics
        statisticsPeriodic = STWJob.STWJob(1)       # 1 secs
        statisticsPeriodic.startJob(CurrentEt)

        # set default target
        self.astroguide.SetActual(CurrentEt, self.mount.Axis0_Angle(), self.mount.Axis1_Angle())
        self.astroguide.SetTarget(CurrentEt, self.astroguide.Actual.ra, self.astroguide.Actual.de)

        # set default angular tracking speed degs/s
        self.lonps, self.latps = self.astroguide.EstimateTargetAngularSpeed()

        while not self.ControlCDetected:
            CurrentEt = self.astroguide.GetSecPastJ2000TDBNow(offset = self.TimeOffsetSec)

            # process user input
            self.DoUserControlJob(CurrentEt)

            # update target and actual telescope state
            # do periodic ...                  
            if loopPeriodic.doJob(CurrentEt):
                # process stellarium input
                self.DoStellariumInput(CurrentEt)

            if stellariumPeriodicSend.doJob(CurrentEt):
                # process stellarium output
                self.DoStellariumOutput()

            if statisticsPeriodic.doJob(CurrentEt):
                with Timer('SetActual'):
                    self.astroguide.SetActual(CurrentEt, self.mount.Axis0_Angle(), self.mount.Axis1_Angle())

                self.log.debug(
                    "Telescope Target %f,%f", self.astroguide.Target.lon, self.astroguide.Target.lat)
                self.log.debug(
                        "Telescope Actual %f,%f", self.astroguide.Actual.lon, self.astroguide.Actual.lat)
                
