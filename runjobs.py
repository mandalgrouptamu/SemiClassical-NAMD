import os
import numpy as np
import itertools
import sys 

RED = '\033[31m'
GREEN = '\033[32m'
RESET = '\033[0m'

thisFile = (os.path.basename(__file__))


folder_name = sys.argv[1]
folderexist = os.path.exists(folder_name)
os.system(f"mkdir -p {folder_name}")

if not folderexist:
    os.system(f"cp {thisFile} ./{folder_name}/")

os.chdir(folder_name)

amu, ps, cm, Å =  1836.0, 41341.37, 1/0.000004556, 1.8897259885789 # unit conversion factors
#------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------
base = "/scratch/user/u.am105188/GP/Nex=1/polaritonGP_original/clean"
Nex = np.arange(100,3000,500)
#γ  = 1.46e-4 * np.array([0.0, 1.0, 1.5, 2.0]) 
scans = [['Nex']] 


overWriteParams = {
    'NTraj' : 25,
    'γ' : 1.46e-4,
    'U' : 0.0,
    'E0' : 2.7/27.2114,
    'ω' : 360/cm
}
#------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------
files = ["serial.py", "initialMC.py", "run.py", "input.txt", "avg.py", "plt.py"]
submitScripts = ['initialMC.py', 'run.py', 'avg.py', 'plt.py']
#------------------------------------------------------------------------------------------


files, submitScripts = list(files), list(submitScripts)
print( f"\n{RED}IMPORTANT: Using base as", base, f"\n{RESET}" + f"\n")
folderHierarchy = []
for folderLevel  in range(len(scans)):
    paramsList =  scans[folderLevel]
    fnames = []
    if len(paramsList) > 1:
        command = f"paramComb = list(itertools.product({','.join(paramsList)}))"
        exec(command)
        
        #print(paramsList, paramComb)
        for i in range(len(paramComb)):
            foldername = ""
            for j in range(len(paramsList)):
                foldername += f"{paramsList[j]}={paramComb[i][j]}_"
            fnames.append(foldername[:-1])
            #print(foldername[:-1])
    else: 
        #print("__________")
        command = f"paramComb = {paramsList[0]}"
        exec(command)

        for i in range(len(paramComb)): 
            foldername = f"{paramsList[0]}={paramComb[i]}"
            fnames.append(foldername)
            #print(foldername)
 
    folderHierarchy.append(fnames)


def getInput(input,key):
    try:
        txt = [i for i in input if i.find(key)!=-1][0].split("=")[1].split("#", 1)[0].replace("\n","")
    except:
        txt = ""
    return txt.replace(" ","")

allFolders = ["/".join(i) for i in list(itertools.product(*folderHierarchy))]



inputtxt = open(f'{base}/input.txt', 'r').readlines()
model =  getInput(inputtxt,"Model")
method = getInput(inputtxt,"Method").split("-")[0]
cwd = os.getcwd()

inputprint = "\n".join([f'{i+1}. {submitScripts[i]}' for i in range(len(submitScripts))])
submitpy = input(f"Which file to submit?\n\n{inputprint}\nPress {1}-{len(submitScripts)} or type N to submit none\n{GREEN}")
pyORsbatch = False
if submitpy != "N": 
    pyORsbatch = input(f"{RESET}Python or sbatch? P/S\n{GREEN}")
makeFolders = input(f"{RESET}Make/overwrite folders? Y/N\n{GREEN}")
print(f"{RESET}")
for fold in allFolders:
    
    if makeFolders == "Y":
        os.system(f"mkdir -p {fold}")
        for f in files:
            os.system(f"cp {base}/{f} {fold}/")
        os.system(f"mkdir -p {fold}/Model")
        os.system(f"mkdir -p {fold}/Method")
        os.system(f"cp -r {base}/Model/{model}.py {fold}/Model/")
        os.system(f"cp -r {base}/Method/{method}.py {fold}/Method/")
        if "input.txt" in files:
            # edit Input
            inp_file = open(f"{fold}/input.txt", "a")
            params = fold.replace("_","/").split("/")
            for i in range(len(params)):
                inp_file.write(f"${params[i]}\n")

            for key in overWriteParams:
                inp_file.write(f"${key}={overWriteParams[key]}\n")
            inp_file.close()

    os.chdir(fold)
    if submitpy != "N":
        if pyORsbatch == "P":
            os.system(f"python {submitScripts[int(submitpy)-1]}")
        elif pyORsbatch == "S":
            os.system(f"sbatch {submitScripts[int(submitpy)-1]}")
    os.chdir(cwd)