\begindata

PATH_VALUES  = ( 'data/naif',
                 'data/user' )
 
PATH_SYMBOLS = ( 'GENERIC_KERNELS',
                    'USER_KERNELS' )

KERNELS_TO_LOAD = ( 
'$GENERIC_KERNELS/naif0012.tls', 
'$GENERIC_KERNELS/pck00010.tpc', 
'$GENERIC_KERNELS/earth_200101_990628_predict.bpc'
'$USER_KERNELS/kiel.tf',
'$USER_KERNELS/kiel.bsp',
'$USER_KERNELS/telescope.tf',
)
\begintext

Add '$GENERIC_KERNELS/de440.bsp' to KERNELS_TO_LOAD if SPK objects needed
