
# Automated download of NAIF data for spiceypy 

import wget, os

JPLServer = "ftp://naif.jpl.nasa.gov/"

BaseDirectory = "pub/naif/generic_kernels/"
PCKDirectory            = "pck/"
LSKDirectory            = "lsk/"
SPKPlanetsDirectory     = "spk/planets/"
UtilDirectory           = "pub/naif/utilities/PC_Windows_64bit/"


LSKFile     = "naif0012.tls"
TPCFile     = "pck00010.tpc"
BPCFile     = "earth_200101_990825_predict.bpc"
DE440File   = "de440.bsp"
# PinpointExe = "pinpoint.exe"
# BriefExe    = "brief.exe"

DestinationDir          = "./data/naif/"
DestinationDirUser      = "./data/user"

def DownloadFile(externalPath, localPath, fname):
    if not os.path.exists(localPath + fname):
        wget.download(externalPath + fname, localPath)
    else:
        print(localPath + fname + " exsists already. Skipped")

DownloadFile(JPLServer + BaseDirectory + LSKDirectory,          DestinationDir, LSKFile)
DownloadFile(JPLServer + BaseDirectory + PCKDirectory,          DestinationDir, TPCFile)
DownloadFile(JPLServer + BaseDirectory + PCKDirectory,          DestinationDir, BPCFile)
DownloadFile(JPLServer + BaseDirectory + SPKPlanetsDirectory,   DestinationDir, DE440File)

# Does not work on Windows because of LF to CRLF wget
# So use compiled kiel.bsp or convert kiel.def and pck00010.tpc
#
# DownloadFile(JPLServer + UtilDirectory,                         DestinationDirUser, PinpointExe)
# DownloadFile(JPLServer + UtilDirectory,                         DestinationDirUser, BriefExe)

