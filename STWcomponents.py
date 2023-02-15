# -*- coding: utf-8 -*-
""" STWcomponents module of the observator project.

This module abstracts stellarium functions.

Todo:

"""

import STWobject, STWsystem, STWastrometry, STWusercontrol, STWstellarium, STWJob, STWMotors

import json

from signal import signal, SIGINT

class components(STWobject.stwObject):
    def __init__(self, logger):
        super().__init__(logger)

        self.sys        = STWsystem.sys(self.log)
        self.astro      = STWastrometry.astro(self.log)
        self.astroguide = STWastrometry.astroguide(self.log)
        self.uc         = STWusercontrol.uc(self.log)
        self.stellarium = STWstellarium.stellarium(self.log)
        self.mount      = STWMotors.mount(self.log)

        self.TimeOffsetSec = 0

        self.TelescopeWestPier = True
        
        self.SlewSpeedFactor   = 0.1  # fraction of max speed

        self.IsMountTracking = False

# start basic initialisation phase
    def Init(self):
        self.log.info("Start basic initialisation phase.")

        self.sys.Init()
        self.astro.Init()
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

        self.astro.Config()
        self.astroguide.Config()
        self.uc.Config()
        self.sys.Config()
        self.stellarium.Config()
        self.mount.Config()

        # try to get time offset to system time via NTP
        ret = self.sys.GetNtpOffsetSec()
        self.TimeOffsetSec = ret[1]
        if ret[0]:
            self.log.info("Time offset to NTP Server is %3.2fs", self.TimeOffsetSec)
        else:   
            self.log.info("Unable to detect time offset to NTP Server")

        # angular tracking speed degs/s    
        self.lonps = 0
        self.latps = 0

        return super().Config()

    def PreLoop(self):
        self.log.info("Start preloop phase.")

    def ExitLoop(self):
        self.log.info("Start exit loop phase.")

    def Shutdown(self):
        self.log.info("Start shutdown phase.")
        
        self.astro.Shutdown()
        self.astroguide.Shutdown()
        self.uc.Shutdown()
        self.sys.Shutdown()
        self.stellarium.Shutdown()
        self.mount.Shutdown()

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
                #           A   is not defined

            match remote:
                case 'S1':
                    self.log.debug("Slew telescope to target.")
                    self.mount.Axis0_SlewTo(self.astroguide.Target.lon)
                    self.mount.Axis1_SlewTo(self.astroguide.Target.lat)

                case 'S2':
                    self.log.debug("Set telescope reference.")
                    self.mount.Axis0_SetAngle(self.astroguide.Target.lon)
                    self.mount.Axis1_SetAngle(self.astroguide.Target.lat)

                case 'XC':
                    self.mount.Axis0_SoftStop()
                case 'XR':
                    self.mount.SlewConstantSpeed(0, self.SlewSpeedFactor, self.mount.Axis0_GetMaxSpeed(), 1)
                case 'XL':
                    self.mount.SlewConstantSpeed(0, self.SlewSpeedFactor, self.mount.Axis0_GetMaxSpeed(), -1)
                case 'YC':
                    self.mount.Axis1_SoftStop()
                case 'YU':
                    self.mount.SlewConstantSpeed(1, self.SlewSpeedFactor, self.mount.Axis1_GetMaxSpeed(), 1)
                case 'YD':
                    self.mount.SlewConstantSpeed(1, self.SlewSpeedFactor, self.mount.Axis1_GetMaxSpeed(), -1)
 
                case 'B':
                    
                    if(self.IsMountTracking):
                        self.log.debug("Stop constant speed tracking")
                        self.IsMountTracking = False
                        self.mount.SoftStopMotors()
                    else:
                        self.log.debug("Start constant speed tracking")
                        self.IsMountTracking = True
                        self.mount.SetConstantSpeed(self.lonps, self.latps)

                case 'D':
                    self.log.debug("D user control command received.")
                case 'C':
                    self.log.debug("C user control command received.")
                case 'A':
                    try:
                        datafile =  open("datadata.json",'r+')
                        file_data = json.load(datafile)
                    except FileNotFoundError:
                        # if not existe create new and start over
                        datafile =  open("datadata.json",'w+')
                        file_data = {}
                        file_data["data"] = []                       
                    finally:
                        # update 
                        self.astroguide.SetActual(CurrentEt, self.mount.Axis0_Angle(), self.mount.Axis1_Angle(), Aligned2WestPier=self.TelescopeWestPier)
      
                        state = {   "et":               CurrentEt,
                                    "UTC":              self.astroguide.GetUTCTimeStrFromEt(CurrentEt),    
                                    "TelescopeLon":     self.astroguide.Actual.lon,  
                                    "TelescopeLat":     self.astroguide.Actual.lat,
                                    "TargetLon":        self.astroguide.Target.lon,
                                    "TargetLat":        self.astroguide.Target.lat,
                                    "TargetRa":         self.astroguide.Target.ra,
                                    "TargetDe":         self.astroguide.Target.de,
                                    "IsWestPier":       self.TelescopeWestPier }

                        file_data["data"].append(state)
                        # overwrite file contents
                        datafile.truncate(0)
                        datafile.seek(0)

                        json.dump(file_data, datafile, indent = 4)
                        datafile.close()

                case _: self.log.error("Undefinded user control command %s received.", remote)

    def DoStellariumInput(self, CurrentEt):
        ret, ra, de  = self.stellarium.ReceiveFromStellarium()
        if ret:
            self.astroguide.SetTarget(CurrentEt, ra, de, Aligned2WestPier=self.TelescopeWestPier)
    
    def DoStellariumOutput(self, CurrentEt):
        # Simulation reflects target lon, lat
        self.stellarium.SendToStellarium(self.astroguide.Actual.ra, self.astroguide.Actual.de)

    def Loop(self):
        self.log.info("Start loop phase.")

        CurrentEt = self.astro.GetSecPastJ2000TDBNow(offset = self.TimeOffsetSec)

        # loop periodic 
        loopPeriodic = STWJob.STWJob(0.1)           # 0.1 secs
        loopPeriodic.startJob(CurrentEt)

        stellariumPeriodicSend = STWJob.STWJob(0.5) # 0.5 secs 
        stellariumPeriodicSend.startJob(CurrentEt)

        statisticsPeriodic = STWJob.STWJob(2) # 2 secs
        statisticsPeriodic.startJob(CurrentEt)

        # set default target
        self.astroguide.SetActual(CurrentEt, self.mount.Axis0_Angle(), self.mount.Axis1_Angle(), Aligned2WestPier=self.TelescopeWestPier)
        self.astroguide.SetTarget(CurrentEt, self.astroguide.Actual.ra, self.astroguide.Actual.de, Aligned2WestPier=self.TelescopeWestPier)

        # set default angular tracking speed degs/s
        self.lonps, self.latps = self.astroguide.EstimateTargetAngularSpeed(Aligned2WestPier=self.TelescopeWestPier)

        while not self.ControlCDetected:
            CurrentEt = self.astro.GetSecPastJ2000TDBNow(offset = self.TimeOffsetSec)

            # do periodic ...
            if loopPeriodic.doJob(CurrentEt):
                # process user input
                self.DoUserControlJob(CurrentEt)
   
                # process stellarium input
                self.DoStellariumInput(CurrentEt)

                # check mount for errors
                self.mount.CheckErrors()

                # update target and actual telescope state    
                self.astroguide.SetTarget(CurrentEt, self.astroguide.Target.ra, self.astroguide.Target.de, Aligned2WestPier=self.TelescopeWestPier)
                self.astroguide.SetActual(CurrentEt, self.mount.Axis0_Angle(), self.mount.Axis1_Angle(), Aligned2WestPier=self.TelescopeWestPier)
 
            if stellariumPeriodicSend.doJob(CurrentEt):
                # process stellarium output
                self.DoStellariumOutput(CurrentEt)

            if statisticsPeriodic.doJob(CurrentEt):
                self.log.debug("Telescope Target %f,%f", self.astroguide.Target.lon, self.astroguide.Target.lat)
                self.log.debug("Telescope Actual %f,%f", self.astroguide.Actual.lon, self.astroguide.Actual.lat)
