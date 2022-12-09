# -*- coding: utf-8 -*-
""" STWastrometry module of the observator project.

This module abstracts astrometry functions.

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

import spiceypy
from datetime   import datetime
from math       import floor

class astro(STWobject.stwObject):
    
    def Init(self):
        self.log.info("Initialize Astrometry.")
        return super().Init()

    def Config(self, fname = 'standart.tm'):
        self.log.info("Load text kernel " + fname + " for spiceypy.")
        
        try:
            spiceypy.furnsh(fname)
        except:
            self.log.error("Failed to load text kernel " + fname)
        else:
            self.isConfigured = True

        return super().Config()

    def Shutdown(self):
        spiceypy.kclear()
        return super().Shutdown()

    def GetUTCNowTimeStringNow(self):
        return datetime.now().utcnow().strftime("%Y-%m-%d %H:%M:%S.%f") + " (UTC)"

    def GetSecPastJ2000TDBNow(self, str = None, offset = 0):
        if str:
            et = spiceypy.str2et(str)
        else:
            et = spiceypy.str2et(self.GetUTCNowTimeStringNow())
        return et + offset

    def RaDeJ20002LonLatAzmimutal(self, et, ra_deg, de_deg):
        __, Lon, Lat = spiceypy.recrad(spiceypy.mxv(spiceypy.pxform('J2000', 'AZ_TOPO', et), \
            spiceypy.latrec(1, ra_deg * spiceypy.rpd(), de_deg* spiceypy.rpd())));  
        return Lon * spiceypy.dpr(), Lat * spiceypy.dpr()

    def RaDeJ20002LonLatTelescope(self, et, ra_deg, de_deg, Aligned2WestPier = True):
        if Aligned2WestPier:
            frame = 'WEST_TOPO'
        else:
            frame = 'EAST_TOPO'

        __, Lon, Lat = spiceypy.recrad(spiceypy.mxv(spiceypy.pxform('J2000', frame, et), \
            spiceypy.latrec(1, ra_deg * spiceypy.rpd(), de_deg* spiceypy.rpd())));

        # because telescope is running from east to west treat Lon as negative before meridian 
        if Lon > spiceypy.pi():
            Lon = Lon - 2*spiceypy.pi()

        return Lon * spiceypy.dpr(), Lat * spiceypy.dpr()

    def LonLatTelescope2RaDeJ2000(self, et, Lon_deg, Lat_deg, Aligned2WestPier = True):
        if Aligned2WestPier:
            frame = 'WEST_TOPO'
        else:
            frame = 'EAST_TOPO'

        __, ra, de = spiceypy.recrad(spiceypy.mxv(spiceypy.pxform(frame, 'J2000', et), \
            spiceypy.latrec(1, Lon_deg * spiceypy.rpd(), Lat_deg* spiceypy.rpd()))); 
        return ra * spiceypy.dpr(), de * spiceypy.dpr()

    def SPK2RaDeJ2000(self, et, idstr):
        pos, __ = spiceypy.spkpos(idstr, et, 'J2000', 'lt+s', 'KIELSTW')
        __, ra, de = spiceypy.recrad(pos)
        return ra * spiceypy.dpr(), de * spiceypy.dpr()


    def ddeg2dms(self, a, chdeg = 'd'):
        if a >= 0:
            ss = '+'
        else:
            ss = '-'
            a = -a;

        d = floor(a)
        a = 60.0*(a - d)
        m = floor(a)
        a = 60.0*(a - m)
        s = floor(a)
        f = floor(100.0*(a - s))
        
        return "{0:s}{1:03d}{degChar}{2:02d}m{3:02d}.{4:02d}s".format(ss, d,  m, s, f, degChar = chdeg)

    def GetJ2000CoordsString(self, ra, de):
        return self.ddeg2dms(ra/15, chdeg = 'h') + " " + self.ddeg2dms(de)

    def GetTelescopeCoordsString(self, lon, lat):
        return self.ddeg2dms(lon) + " " + self.ddeg2dms(lat)

    def GetAzimutalCoordsString(self, long, lat):
        return self.ddeg2dms(long) + " " + self.ddeg2dms(lat)
        
import logging

def main():

    a = astro(logging.getLogger())
    
    a.Config()

    timeStr = "2022-12-03 12:00:03.318539 (UTC+1)"  # a.GetUTCNowTimeStringNow()

    print(timeStr)

    et = a.GetSecPastJ2000TDBNow(timeStr)

    ra, de = a.SPK2RaDeJ2000(et, 'sun')

    print("Object J2000    : " + a.GetJ2000CoordsString(ra, de))

    lon, lat = a.RaDeJ20002LonLatAzmimutal(et, ra, de)

    print("Object Azimutal : " + a.GetAzimutalCoordsString(lon, lat))

    lon, lat = a.RaDeJ20002LonLatTelescope(et, ra, de)

    print("Object Telescope: " + a.GetTelescopeCoordsString(lon, lat))

    ra, de = a.LonLatTelescope2RaDeJ2000(et, lon, lat)

    print("Object J2000    : " + a.GetJ2000CoordsString(ra, de) + " from lon, lat telescope")

    lon, lat = a.RaDeJ20002LonLatTelescope(et, ra, de, False)
 
    print("Object Telescope: " + a.GetTelescopeCoordsString(lon, lat) + " East Pier")

    ra, de = a.LonLatTelescope2RaDeJ2000(et, lon, lat, False)

    print("Object J2000    : " + a.GetJ2000CoordsString(ra, de) + " from East Pier and lon, lat telescope")

if __name__ == "__main__":
    main()