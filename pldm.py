import numpy as np
import model

dt = model.parameters.dt
NSteps = model.parameters.NSteps
NGrid = model.parameters.NGrid

# Initialization of the mapping Variables
def initMapping(Nstates, initState = 0, stype = "focused"):
    #global qF, qB, pF, pB, qF0, qB0, pF0, pB0
    qF = np.zeros((Nstates))
    qB = np.zeros((Nstates))
    pF = np.zeros((Nstates))
    pB = np.zeros((Nstates))
    if (stype == "focused"):
        qF[initState] = 1.0
        qB[initState] = 1.0
        pF[initState] = 1.0
        pB[initState] = -1.0 # This minus sign allows for backward motion of fictitious oscillator
    else:
       qF = np.array([ np.random.normal() for i in range(Nstates)]) 
       qB = np.array([ np.random.normal() for i in range(Nstates)]) 
       pF = np.array([ np.random.normal() for i in range(Nstates)]) 
       pB = np.array([ np.random.normal() for i in range(Nstates)]) 
    return qF, qB, pF, pB 

def propagateMapVars(qF, qB, pF, pB, dt):
    qFin, qBin, pFin, pBin = qF, qB, pF, pB # Store input position and momentum for verlet propogation
    # Store initial array containing sums to use at second derivative step
    VMatxqB =  np.array([np.sum(VMat[k,:] * qBin[:]) for k in range(NStates)])
    VMatxqF =  np.array([np.sum(VMat[k,:] * qFin[:]) for k in range(NStates)])
    for i in range(NStates): # Loop over q's and p's for initial update of positions
       # Update momenta using input positions (first-order in dt)
       pB[i] -= 0.5 * dt * np.sum(VMat[i,:] * qBin[:]) ## First Derivatives ##
       pF[i] -= 0.5 * dt * np.sum(VMat[i,:] * qFin[:])
       # Now update positions with input momenta (first-order in dt)
       qB[i] += dt * np.sum(VMat[i,:] * pBin[:])
       qF[i] += dt * np.sum(VMat[i,:] * pFin[:])
       for k in range(NStates):
           # Update positions to second order in dt
           qB[i] -= (dt**2/2.0) * (VMat[i,k])* VMatxqB[k] ## Second Derivatives ##
           qF[i] -= (dt**2/2.0) * (VMat[i,k])* VMatxqF[k]
    
    # Update momenta using output positions (first-order in dt)
    for i in range(NStates): # Loop over q's and p's for final update of fictitious momentum
       pB[i] -= 0.5 * dt * np.sum(VMat[i,:] * qB[:])
       pF[i] -= 0.5 * dt * np.sum(VMat[i,:] * qF[:])
    return qF, qB, pF, pB

def propagateMapVarsMarcus(qF, qB, pF, pB, dt):
    qFin, qBin, pFin, pBin = qF, qB, pF, pB # Store input position and momentum for verlet propogation
    # Store initial array containing sums to use at second derivative step
    VMatxqB =  np.array([np.sum(VMat[k,:] * qBin[:]) for k in range(NStates)])
    VMatxqF =  np.array([np.sum(VMat[k,:] * qFin[:]) for k in range(NStates)])
    for i in range(NStates): # Loop over q's and p's for initial update of positions
       # Update momenta using input positions (first-order in dt)
       pB[i] -= 0.5 * dt * np.sum(VMat[i,:] * qBin[:]) ## First Derivatives ##
       pF[i] -= 0.5 * dt * np.sum(VMat[i,:] * qFin[:])
       # Now update positions with input momenta (first-order in dt)
       qB[i] += dt * np.sum(VMat[i,:] * pBin[:])
       qF[i] += dt * np.sum(VMat[i,:] * pFin[:])
       for k in range(NStates):
           # Update positions to second order in dt
           qB[i] -= (dt**2/2.0) * (VMat[i,k])* VMatxqB[k] ## Second Derivatives ##
           qF[i] -= (dt**2/2.0) * (VMat[i,k])* VMatxqF[k]
    
    # Update momenta using output positions (first-order in dt)
    for i in range(NStates): # Loop over q's and p's for final update of fictitious momentum
       pB[i] -= 0.5 * dt * np.sum(VMat[i,:] * qB[:])
       pF[i] -= 0.5 * dt * np.sum(VMat[i,:] * qF[:])
    return qF, qB, pF, pB



def getPopulation(qF, qB, pF, pB, qF0, qB0, pF0, pB0, step):
    print (step/NSteps * 100, "%")
    rho = np.zeros(( len(qF), len(qF) ), dtype=complex) # Define density matrix
    rho0 = (qF0 - 1j*pF0) * (qB0 + 1j*pB0)
    file01.write(str(step))
    file03.write(str(step))
    for i in range(len(qF)):
       for j in range(len(qF)):
          if (j >= i and i != j):
              rho[i,j] = 0.25 * (qF[i] + 1j*pF[i]) * (qB[j] - 1j*pB[j]) * rho0
              file01.write("\t" + str(rho[i,j].real))
              if (i == j):
                file03.write("\t" + str(rho[i,j].real))
              if (i == j and i == NStates-1):
                file03.write("\t" + str(np.sum(rho[i,i].real for i in range(len(rho)))) + "\n")
                file01.write("\n")


    return rho


## Start Main Program

#VMat = model.HelTwoLevel() # Get interaction Hamiltonian from model file
VMat = model.HelEqualEnergyManifold(2) # NEW EXPERIMENT ~BMW
VMat = model.HelMarcusTheory(NGrid) # Marcus theory -- Two Parabolas
NStates = len(VMat) # This is the dimension of the interaction hamiltonian.
initState = 0 # Choose (arbitrarily???) the initial state of the particle population. To see "relaxation" of particle population, should be high-energy state in VMat.
qF, qB, pF, pB = initMapping(NStates,initState) # Call function to initialize fictitious oscillators according to focused ("Default") or according to gaussian random distribution
qF0, qB0, pF0, pB0 = qF[initState], qB[initState], pF[initState], pB[initState] # Set initial values of fictitious oscillator variables for future use

file01 = open("output_rho.txt","w") # Density natrix: Step, 11, 12, 13, 14, 22, 23, 24, 33, 34, 44, or similar for upper triangle of NxN matrix, SUM_OF_DIAGS
file03 = open("output_rho_diags.txt","w")
#file02 = open("output_map.txt","w") # Fictitious Oscillator Motion (Use for sanity check): Step, qF[0], PF

for i in range(NSteps):
    if (i % 1000 == 0):
        rho_current = getPopulation(qF, qB, pF, pB, qF0, qB0, pF0, pB0, i)
    qF, qB, pF, pB = propagateMapVars(qF, qB, pF, pB, dt)
file01.close()
#file02.close()

Hmap = model.getForce(VMat, qF, qB, pF, pB)
print (Hmap)


## OLD CODE: ##   
#file01.write( str(i) + "\t" + "\t".join(rho_current.flatten().real.astype("str")) + "\t" + str(np.sum(rho_current[i,i].real for i in range(len(rho_current)))) + "\n")
#file02.write( str(i) + "\t" + str(qF[0]) + "\t" + str(pF[0]) + + "\t" + str(qB[0]) + "\t" + str(pB[0]) + "\n")




