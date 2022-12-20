
# Download public data from JPL 

import wget, os

JPLServer = "ftp://naif.jpl.nasa.gov/"

BaseDirectory = "pub/naif/generic_kernels/"
PCKDirectory            = "pck/"
LSKDirectory            = "lsk/"
SPKPlanetsDirectory     = "spk/planets/"

LSKFile     = "naif0012.tls"
TPCFile     = "pck00010.tpc"
BPCFile     = "earth_200101_990628_predict.bpc"
DE440File   = "de440.bsp"

DestinationDir          = "./data/naif/"

def DownloadFile(externalPath, localPath, fname):
    if not os.path.exists(localPath + fname):
        wget.download(externalPath + fname, localPath)
    else:
        print(localPath + fname + " exsists already. Skipped")

DownloadFile(JPLServer + BaseDirectory + LSKDirectory,          DestinationDir, LSKFile)
DownloadFile(JPLServer + BaseDirectory + PCKDirectory,          DestinationDir, TPCFile)
DownloadFile(JPLServer + BaseDirectory + PCKDirectory,          DestinationDir, BPCFile)
DownloadFile(JPLServer + BaseDirectory + SPKPlanetsDirectory,   DestinationDir, DE440File)
