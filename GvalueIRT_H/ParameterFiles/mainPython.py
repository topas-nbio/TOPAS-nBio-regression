############################
### Import Libraries

import numpy as np
import subprocess
import sys 
from os import system as command

############################
### Define Main

def Main():
    TOPAS = sys.argv[1]
    Concentrations = ["1e-2", "1e-1", "300e-3", "1e-0"]

    for c in Concentrations:
        command("sed 's/theConcentration/'%s'/g' HydrogenAtom1mM.txt > run1mM.txt" % c)
        subprocess.call([TOPAS, "run1mM.txt"])
        command("mv run1mM.txt run1mM_%s.txt"%(c))

    command("cp HydrogenAtom_dirty.txt run_dirty.txt")
    subprocess.call([TOPAS, "run_dirty.txt"])

############################
### Run Main

if __name__=="__main__":
    Main()

############################
