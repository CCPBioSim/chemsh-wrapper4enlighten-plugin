## chemsh-wrapper4enlighten-plugin

This repository contains the python script (qmmm.py) and a Docker file to run ChemShell (chemshell.org) as part of the Enlighten2 PyMol-plugin (https://enlighten2.github.io)

The qmmm.py script expects that the coordinates and topology of the system along with a parameters file will be in the directory where the script is run.
It will then produce a Py-ChemShell input file in that directory and a chemshell subdirectory where all the output from ChemShell will be saved.
DL\_POLY is used for the MM part and the user can select the code for the QM part (tested with DFTB+ and MNDO).

The script works for three types of calculation: single point energy (sp), geometry optimisation (opt), or nudged elastic band reaction profiling (neb).

Parameters for the QM/MM calculation are passed in through a json formatted file.
For most of the parameters default values have been set (hopefully sensible ones), but the QM region must be defined by the user.

The topology file is expected to have an Amber format and include the list of partial charges for all atoms in the system.

Single point and geometry optimisation calculations expect one input structure.
NEB calculations require two structures, one for each end point of the reaction path.

# Usage

qmmm.py type params parmtop reactants -p products

    type = sp or opt or neb, which kind of calculation

    params = json file with parameters

    parmtop = topology file (Amber format)

    reactants = structure file

    -p products = optional structure file (not used for sp/opt, needed for neb)

# Parameters for ChemShell calculation
qm\_engine : which QM code to use, default DFTBplus

qm\_path : tells ChemShell where the QM code is, default '~/dftb/bin/dftb+'

skf\_path : only for DFTPplus, where are the parameter files, default '~/dftb/slakos/mio-1-1/'

qm\_method : not for DFTBplus, default am1

multiplicity : default 1

scftype : default rhf

maxcycles : default 100

nimages : for neb, default 100

climbing\_image : for neb, default yes

qm\_region : which atoms should be in the QM calcution, no default = MUST be set by the user

qm\_charge : the charge of the qm\_region, no default

active\_region : for opt/neb, default = qm\_region
