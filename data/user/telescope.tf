KPL/PCK

\begintext
===========
Prof. Rinder 03.09.2022 thomas.rinder@fh-kiel.de
===========
Definitions
===========

COORD_TOPO is a frame which is aligned to the earth rotation axis in z-axis
as DYNSTW_TOPO does. x-Axis is mirrored to DYNSTW_TOPO. 
So telescope is moving from east to west with increasing longitude.
Adjust TKFRAME_COORD_TOPO_ANGLES if not aligned (telescope mount alignment).

WEST_TOPO is aligned to COORD_TOPO. 

The telescope is slewing in WEST_TOPO frame in latitudional coordinates
which depends on COORD_TOPO as needed for "West side of pier".

EAST_TOPO is the same frame as WEST_TOPO but z-axis is mirrored.
So altitude is negative as needed for "East side of pier".
 
===========
=> Telescope modes:

WEST_TOPO is "West side of pier" telescope mode.
EAST_TOPO is "East side of pier" telescope mode.

===========
Remark:
So use WEST_TOPO or EAST_TOPO consequently instead of COORD_TOPO or DYNSTW_TOPO or something else 
because the model of alignment from DYNSTW_TOPO to WEST_TOPO may change.
===========


\begindata

NAIF_BODY_NAME+='WEST_TOPO'
NAIF_BODY_CODE+=399898

NAIF_BODY_NAME+='EAST_TOPO'
NAIF_BODY_CODE+=399897

NAIF_BODY_NAME+='AZ_TOPO'
NAIF_BODY_CODE+=399895

NAIF_BODY_NAME+='CC_TOPO'
NAIF_BODY_CODE+=399894

NAIF_BODY_NAME+='COORD_TOPO'
NAIF_BODY_CODE+=399893

FRAME_WEST_TOPO                  = 1399898
FRAME_1399898_NAME               = 'WEST_TOPO'
FRAME_1399898_CLASS              = 4
FRAME_1399898_CLASS_ID           = 1399898
FRAME_1399898_CENTER             = 399893

OBJECT_399898_FRAME              = 'WEST_TOPO'
TKFRAME_WEST_TOPO_RELATIVE       = 'COORD_TOPO'
TKFRAME_WEST_TOPO_SPEC           = 'ANGLES'
TKFRAME_WEST_TOPO_UNITS          = 'DEGREES'
TKFRAME_WEST_TOPO_AXES           = ( 3,   1, 	2)
TKFRAME_WEST_TOPO_ANGLES         = ( 0,   0, 	0)

FRAME_EAST_TOPO                  = 1399897
FRAME_1399897_NAME               = 'EAST_TOPO'
FRAME_1399897_CLASS              = 4
FRAME_1399897_CLASS_ID           = 1399897
FRAME_1399897_CENTER             = 399898

OBJECT_399897_FRAME              = 'EAST_TOPO'
TKFRAME_EAST_TOPO_RELATIVE       = 'WEST_TOPO'
TKFRAME_EAST_TOPO_SPEC           = 'MATRIX'
TKFRAME_EAST_TOPO_MATRIX         = (1,0,0,
                                    0,1,0,
                                    0,0,-1)

FRAME_AZ_TOPO                    = 1399896
FRAME_1399896_NAME               = 'AZ_TOPO'
FRAME_1399896_CLASS              = 4
FRAME_1399896_CLASS_ID           = 1399896
FRAME_1399896_CENTER             = 399899

OBJECT_399896_FRAME              = 'AZ_TOPO'
TKFRAME_AZ_TOPO_RELATIVE         = 'KIELSTW_TOPO'
TKFRAME_AZ_TOPO_SPEC             = 'MATRIX'
TKFRAME_AZ_TOPO_MATRIX           = (-1,0,0,
                                     0,1,0,
                                     0,0,1)

FRAME_CC_TOPO                   = 1399894
FRAME_1399894_NAME              = 'CC_TOPO'
FRAME_1399894_CLASS             = 4
FRAME_1399894_CLASS_ID          = 1399894
FRAME_1399894_CENTER            = 399899

OBJECT_399894_FRAME             = 'CC_TOPO'
TKFRAME_CC_TOPO_RELATIVE        = 'DYNSTW_TOPO'
TKFRAME_CC_TOPO_SPEC            = 'MATRIX'
TKFRAME_CC_TOPO_MATRIX          = ( 1,0,0,
                                    0,1,0,
                                    0,0,1)

FRAME_COORD_TOPO                = 1399893
FRAME_1399893_NAME              = 'COORD_TOPO'
FRAME_1399893_CLASS             = 4
FRAME_1399893_CLASS_ID          = 1399893
FRAME_1399893_CENTER            = 399894

OBJECT_399893_FRAME             = 'COORD_TOPO'
TKFRAME_COORD_TOPO_RELATIVE     = 'CC_TOPO'
TKFRAME_COORD_TOPO_SPEC         = 'ANGLES'
TKFRAME_COORD_TOPO_UNITS        = 'DEGREES'
TKFRAME_COORD_TOPO_AXES         = ( 3,   1, 	2)
TKFRAME_COORD_TOPO_ANGLES       = ( 0,   0, 	0)

\begintext
