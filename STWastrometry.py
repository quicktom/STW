# -*- coding: utf-8 -*-
""" STWastrometry module of the observator project.

This module abstracts astrometry functions.

Todo:

"""

import logging
import STWobject

import spiceypy
from datetime import datetime
from math import floor, fabs


class astro(STWobject.stwObject):

    kernelLoaded = False    # treat as static to prevent loading kernels multiple times

    def Init(self):
        self.log.info("Initialize Astrometry.")
        return super().Init()

    def Config(self, fname='standart.tm'):
        self.log.info("Load text kernel " + fname + " for spiceypy.")

        if not self.kernelLoaded:
            try:
                spiceypy.furnsh(fname)
            except:
                self.log.error("Failed to load text kernel " + fname)
            else:
                self.isConfigured = True
                self.kernelLoaded = True

        return super().Config()

    def Shutdown(self):
        if self.kernelLoaded:
            spiceypy.kclear()
            self.kernelLoaded = False

        return super().Shutdown()

    @staticmethod
    def GetUTCNowTimeStringNow():
        # Get date time string in UTC frame
        return datetime.now().utcnow().strftime("%Y-%m-%d %H:%M:%S.%f") + " (UTC)"

    @staticmethod
    def GetSecPastJ2000TDBNow(str=None, offset=0):
        # Get secs past epoch 2000 in TDB
        if str:
            et = spiceypy.str2et(str)
        else:
            et = spiceypy.str2et(astro.GetUTCNowTimeStringNow())
        return et + offset

    @staticmethod
    def RaDeJ20002LonLatAzmimutal(et, ra_deg, de_deg):
        # Get oberserver longitude, latidue in local from ra, de in J2000 frame
        __, Lon, Lat = spiceypy.recrad(spiceypy.mxv(spiceypy.pxform('J2000', 'AZ_TOPO', et),
                                                    spiceypy.latrec(1, ra_deg * spiceypy.rpd(), de_deg * spiceypy.rpd())))
        return Lon * spiceypy.dpr(), Lat * spiceypy.dpr()

    @staticmethod
    def RaDeJ20002LonLatTelescope(et, ra_deg, de_deg, Aligned2WestPier=True):
        # Get telescope longitude, latidue from ra, de in J2000 frame
        if Aligned2WestPier:
            frame = 'WEST_TOPO'
        else:
            frame = 'EAST_TOPO'

        __, Lon, Lat = spiceypy.recrad(spiceypy.mxv(spiceypy.pxform('J2000', frame, et),
                                                    spiceypy.latrec(1, ra_deg * spiceypy.rpd(), de_deg * spiceypy.rpd())))

        # warp to negative angle
        if Lon > spiceypy.pi():
            Lon = Lon - 2*spiceypy.pi()

        return Lon * spiceypy.dpr(), Lat * spiceypy.dpr()

    @staticmethod
    def LonLatTelescope2RaDeJ2000(et, Lon_deg, Lat_deg, Aligned2WestPier=True):
        # Get ra,de in J2000 frame from telescope longitude, latitude
        if Aligned2WestPier:
            frame = 'WEST_TOPO'
        else:
            frame = 'EAST_TOPO'

        __, ra, de = spiceypy.recrad(spiceypy.mxv(spiceypy.pxform(frame, 'J2000', et),
                                                  spiceypy.latrec(1, Lon_deg * spiceypy.rpd(), Lat_deg * spiceypy.rpd())))
        return ra * spiceypy.dpr(), de * spiceypy.dpr()

    @staticmethod
    def SPK2RaDeJ2000(et, idstr):
        # Get ra, de in J2000 frame from SPK object
        pos, __ = spiceypy.spkpos(idstr, et, 'J2000', 'lt+s', 'KIELSTW')
        __, ra, de = spiceypy.recrad(pos)
        return ra * spiceypy.dpr(), de * spiceypy.dpr()

    @staticmethod
    def ddeg2dms(a, chdeg='d'):
        # Get string from degree value
        if a >= 0:
            ss = '+'
        else:
            ss = '-'
            a = -a

        d = floor(a)
        a = 60.0*(a - d)
        m = floor(a)
        a = 60.0*(a - m)
        s = floor(a)
        f = floor(100.0*(a - s))

        return "{0:s}{1:03d}{degChar}{2:02d}m{3:02d}.{4:02d}s".format(ss, d,  m, s, f, degChar=chdeg)

    @staticmethod
    def GetJ2000CoordsString(ra, de):
        return astro.ddeg2dms(ra/15, chdeg='h') + " " + astro.ddeg2dms(de)

    @staticmethod
    def GetTelescopeCoordsString(lon, lat):
        return astro.ddeg2dms(lon) + " " + astro.ddeg2dms(lat)

    @staticmethod
    def GetAzimutalCoordsString(lon, lat):
        return astro.ddeg2dms(lon) + " " + astro.ddeg2dms(lat)


class astroguide(STWobject.stwObject):

    def __init__(self, logger, Aligned2WestPier):
        self.log = logger
        self.Aligned2WestPier = Aligned2WestPier

    def Init(self):
        self.telescopeIsAligned = False

        self.astrometry = astro(self.log)
        return super().Init()

    def Config(self):
        self.astrometry.Config()
        return super().Config()

    def Shutdown(self):
        self.astrometry.Shutdown()
        return super().Shutdown()

    def SetTarget(self, et, ra=0, de=0, SPKObjectStr=''):
        # Set target coords from ra, de in J2000 frame or from SPK object
        self.Target = lambda: 0
        # Set target coords from ra,de or SPK object
        self.Target.et = et

        if SPKObjectStr:
            self.Target.ra, self.Target.de = astro.SPK2RaDeJ2000(
                et, SPKObjectStr)
        else:
            self.Target.ra = ra
            self.Target.de = de

        # get telescope coords of target
        self.Target.lon, self.Target.lat = astro.RaDeJ20002LonLatTelescope(
            et, self.Target.ra, self.Target.de, self.Aligned2WestPier)

        # get azimutal coords of target
        self.Target.Azimut = lambda: 0
        self.Target.Azimut.lon, self.Target.Azimut.lat = astro.RaDeJ20002LonLatAzmimutal(
            et, ra, de)

        #self.log.debug("Telescope target is %s (J2000 %s)(Az %s)", 
        #    self.astrometry.GetTelescopeCoordsString(self.Target.lon, self.Target.lat),
        #    self.astrometry.GetJ2000CoordsString(self.Target.ra, self.Target.de),
        #    self.astrometry.GetTelescopeCoordsString(self.Target.Azimut.lon, self.Target.Azimut.lat))    

    def SetActual(self, et, lon, lat):
        # Set actual coords from telescope frame
        self.Actual = lambda: 0
        # Set actual coords from telescope lat, lon
        self.Actual.et = et

        self.Actual.lon = lon
        self.Actual.lat = lat

        # get actual ra de coords
        self.Actual.ra, self.Actual.de = astro.LonLatTelescope2RaDeJ2000(
            et, self.Actual.lon, self.Actual.lat, self.Aligned2WestPier)

        # get azimutal coords of target
        self.Actual.Azimut = lambda: 0
        self.Actual.Azimut.lon, self.Actual.Azimut.lat = astro.RaDeJ20002LonLatAzmimutal(
            et, self.Actual.ra, self.Actual.de)

    def AngularSeparation(self):
        # Get angular separation between target and actual coords
        return spiceypy.vsep(spiceypy.latrec(1, self.Target.ra * spiceypy.rpd(), self.Target.de * spiceypy.rpd()),
                             spiceypy.latrec(1, self.Actual.ra * spiceypy.rpd(), self.Actual.de * spiceypy.rpd())) * spiceypy.dpr()

    def EstimateSlewingTime(self, londps, latdps):
        # Estimate slewing time from actual to target coord position based on average speeds
        # latps, lonps is in degrees per sec
        dlonTime = fabs(self.Target.lon - self.Actual.lon) / londps
        dlatTime = fabs(self.Target.lat - self.Actual.lat) / latdps
        return dlonTime, dlatTime

    def EstimateTargetAngularSpeed(self, dtsec=1):
        # Estimate angular speed of target in degs/s
        tlon1, tlat1 = astro.RaDeJ20002LonLatTelescope(self.Target.et,
                                                       self.Target.ra, self.Target.de, self.Aligned2WestPier)

        tlon2, tlat2 = astro.RaDeJ20002LonLatTelescope(self.Target.et + dtsec,
                                                       self.Target.ra, self.Target.de, self.Aligned2WestPier)

        return (tlon2 - tlon1)/dtsec, (tlat2 - tlat1)/dtsec

    def EstimateSlewingToTargetAngles(self, londps, latdps, dtsec=1):
        # First order estimate of slewing angles from actual to target coords
        # assuming target ra, de coords are constant.
        #
        # If slewing takes a long time then target coords are changing.
        # So the telescope should slew to extimated coords of target.
        tlondps, tlatdps = self.EstimateTargetAngularSpeed(
            dtsec, self.Aligned2WestPier)
        ts = max(self.EstimateSlewingTime(londps, latdps))
        return self.Target.lon + ts * tlondps, self.Target.lat + ts * tlatdps

    def GetUTCTimeStrFromEt(self, et):
        return spiceypy.timout(et, "YYYY-MON-DD HR:MN:SC.# ::UTC ::RND")    
    
    def GetSecPastJ2000TDBNow(self, str=None, offset=0):
        return self.astrometry.GetSecPastJ2000TDBNow(str, offset)
        
def main():

    # a = astro(logging.getLogger())

    # a.Config()

    # timeStr =  a.GetUTCNowTimeStringNow() #"2022-12-03 12:00:03.318539 (UTC+1)"  #

    # print(timeStr)

    # et = a.GetSecPastJ2000TDBNow(timeStr)

    # ra, de = a.SPK2RaDeJ2000(et, 'sun')

    # print("Object J2000    : " + a.GetJ2000CoordsString(ra, de))

    # lon, lat = a.RaDeJ20002LonLatAzmimutal(et, ra, de)

    # print("Object Azimutal : " + a.GetAzimutalCoordsString(lon, lat))

    # lon, lat = a.RaDeJ20002LonLatTelescope(et, ra, de)

    # print("Object Telescope: " + a.GetTelescopeCoordsString(lon, lat))

    # ra, de = a.LonLatTelescope2RaDeJ2000(et, lon, lat)

    # print("Object J2000    : " + a.GetJ2000CoordsString(ra, de) + " from lon, lat telescope")

    # lon, lat = a.RaDeJ20002LonLatTelescope(et, ra, de, False)

    # print("Object Telescope: " + a.GetTelescopeCoordsString(lon, lat) + " East Pier")

    # ra, de = a.LonLatTelescope2RaDeJ2000(et, lon, lat, False)

    # print("Object J2000    : " + a.GetJ2000CoordsString(ra, de) + " from East Pier and lon, lat telescope")

    # a.Shutdown()

    g = astroguide(logging.getLogger())

    g.Init()

    g.Config()

    et = astro.GetSecPastJ2000TDBNow(astro.GetUTCNowTimeStringNow())

    g.SetTarget(et, SPKObjectStr='sun')

    g.SetActual(et, 0, 0)

    print(g.AngularSeparation())

    print(g.EstimateSlewingTime(0.1, 0.1))

    print(g.EstimateTargetAngularSpeed())

    print(g.EstimateSlewingToTargetAngles(0.1, 0.1))

    g.Shutdown()


if __name__ == "__main__":
    main()
