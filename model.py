#def param():

import numpy as np

def Hel():
    vij = np.zeros((2,2))
    vij[0,0] = 0.0
    vij[1,0] = 0.1
    vij[0,1] = 0.1
    vij[0,0] = 2.0
    return vij

#def dHel():
