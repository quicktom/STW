

MountName = 'KeenOne'

match MountName:
    case 'KeenOne'  :
        # KeenOne https://www.printables.com/model/273812-keen-one-harmonic-drive-eq-mount
        # V5 https://www.printables.com/de/model/309144-791-harmonicdrive-for-keen-one-eq
        RAStepsPerRevolution = 79*(26+103/121)*200
        DEStepsPerRevolution = 79*(26+103/121)*200
        RAMotorConfigFile       = 'KeenOne_M0.json'
        DEMotorConfigFile       = 'KeenOne_M1.json'
    case _:
        # default
        # FH Kiel  observatory
        RAStepsPerRevolution    = 270*62.500*100
        DEStepsPerRevolution    = 210*83.333*100
        RAMotorConfigFile       = 'STW_M0.json'
        DEMotorConfigFile       = 'STW_M1.json'


