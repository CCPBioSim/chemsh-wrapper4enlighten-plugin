#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import subprocess

#############################################################################
## To run Py-ChemShell using the structure and topology from the Enlighten ##
## PyMol plugin.                                                           ##
#############################################################################

## utility functions ##
def get_amber_charges(parmtop):
    # This function is to parse an AMBER top file to get a list of partial charges for all the atoms.
    infile = open(parmtop)

    copy = False
    charges = []
    for line in infile:
       if line.startswith("%FLAG CHARGE"):
          copy = True

       elif line.startswith("%FLAG ATOMIC_NUMBER"):
          copy = False

       elif copy:
          if line.startswith("%FORMAT"):
            print("")
          else:
            charge_list = str.split(line)
          # AMBER charges need to be divided by 18.2223 to get the right units for ChemShell
            linecharges = [(float(i) / 18.2223) for i in charge_list]
            charges.extend(linecharges)

    infile.close()
    return charges


## wrapper for Py-ChemShell command ##
class ChemShellWrapper(object):

    def __init__(self, pychemsh, working_directory='chemshell'):

        # get path information as needed
        if os.path.exists(working_directory):
            shutil.rmtree(working_directory)
        os.makedirs(working_directory)
        os.chdir(working_directory)
        
        # get input files
        chemsh_input = ('../'+ pychemsh +'.py')

        # run Py-ChemShell command
        chemshell_command = ('chemsh ' + chemsh_input)
        with open('chemshell.out', 'w') as f:
            proc = subprocess.Popen(chemshell_command, shell=True, stdout=f,
                                stderr=subprocess.STDOUT)
            proc.wait()

## the main part for writing ChemShell input and running ChemShell ##
def main():

    # get input coordinates and topology
    parser = argparse.ArgumentParser(description="Runs a QM/MM calculation\n", formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("type", help="type of calculation: sp, opt, neb")
    parser.add_argument("params", help="JSON file with parameters", type=argparse.FileType())
    parser.add_argument("parmtop", help="topology information", type=argparse.FileType())
    parser.add_argument("reactants", help="file for the initial coordinates of the system", type=argparse.FileType())
    parser.add_argument("-p","-products", help="file for the final coordinates of the system for neb only", type=argparse.FileType())

    args = parser.parse_args()

    # set options for running Py-ChemShell from user input or defaults
    # define qm region - must be specified by user
    # get charges
    # qm code (MNDO or DFTB+)
    # method (AM1, ...)
    # max scf cycles
    # multiplicity
    # nimages is for NEB calculations
    # type of calculation (single point or optimization)
    params = {'qm_engine' : 'DFTBplus', 
            'qm_path' : '~/dftb/bin/dftb+', 
            'skf_path' : '~/dftb/slakos/mio-1-1/',
            'qm_method' : 'am1', 
            'multiplicity' : 1, 
            'scftype' : 'rhf', 
            'maxcycles' : 100, 
            'nimages' : 8, 
            'climbing_image' : 'yes', 
            'qm_region' : [], 
            'qm_charge' : [],
            'active_region' : 'qm_region'}

    if args.params is not None:
        params.update(json.load(args.params))

    qm_region = params['qm_region']
    qm_charge = params['qm_charge']
    qm_engine = params['qm_engine']
    qm_method = params['qm_method']
    multiplicity = params['multiplicity']
    skf_path = params['skf_path']
    qm_path = params['qm_path']
    nimages = params['nimages']
    active_region = params['active_region']

    # read charges from topology file (amber charges must be divided by 18.2223 to get the units right)
    charges = get_amber_charges(args.parmtop.name)

    # create Py-ChemShell input file
    with open('pychemsh.py', 'w') as f:
        f.write("from chemsh import * \n")
        f.write("my_enzyme = Fragment(coords='../{}', charges={})\n".format(args.reactants.name,charges))
        f.write("my_enzyme.save('new.pdb')\n")
        f.write("indicies_qm_region = {}\n".format(qm_region))
        f.write("frag_qm_region = my_enzyme.getSelected(indicies_qm_region)\n")
        f.write("frag_qm_region.save('qm_region.pdb')\n")
        f.write("qm_charge = {}\n".format(qm_charge))
        if qm_engine == 'DFTBplus':
            f.write("my_qm = {}(charge = {}, mult = {}, skf_path='{}', path = '{}',)\n".format(qm_engine,qm_charge,multiplicity,skf_path,qm_path))
        else:
            f.write("my_qm = {}(method = '{}', charge = {}, mult = {}, path = '{}',)\n".format(qm_engine,qm_method,qm_charge,multiplicity,qm_path))
        f.write("my_mm = DL_POLY(ff='../{}', rcut=999.99)\n".format(args.parmtop.name))
        f.write("my_qmmm = QMMM(frag = my_enzyme, qm = my_qm, mm = my_mm, qm_region = indicies_qm_region,)\n")
        if args.type == 'sp':
            f.write("my_sp = SP(theory=my_qmmm)\n")
            f.write("my_sp.run(dryrun=False)\n")
        if args.type == 'opt':
            f.write("my_opt = Opt(theory=my_qmmm, active={})\n".format(active_region))
            f.write("my_opt.run(dryrun=False)\n")
        if args.type == 'neb':
            f.write("product = Fragment(coords='{}')\n".format(args.products.name))
            f.write("product.save('new2.pdb')\n")
            f.write("my_neb = Opt(theory=my_qmmm, active={}, neb='frozen', frag2=product, nimages={}, nebk=0.01, neb_climb_test=3.0, neb_freeze_test=1.0, coordinates='cartesian', maxstep=0.9, trust_radius='const',)\n".format(active_region,nimages))
            f.write("my_neb.run(dryrun=False)\n")


    # run Py-ChemShell
    chemshell = ChemShellWrapper('pychemsh')

if __name__ == '__main__':
    main()
