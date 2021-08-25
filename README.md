# chemsh-wrapper4enlighten-plugin

This repository contains the python script (qmmm.py) and a Docker file to run ChemShell (chemshell.org) as part of the Enlighten2 PyMol-plugin (https://enlighten2.github.io)

Usage:
qmmm.py type params parmtop reactants -p products
    type = sp or opt or neb, which kind of calculation
    params = json file with parameters
    parmtop = topology file (Amber format)
    reactants = structure file
    -p products = optional structure file (not used for sp/opt, needed for neb)
