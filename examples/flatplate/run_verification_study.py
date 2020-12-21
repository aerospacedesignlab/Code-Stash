#!/usr/bin/env python

## \file run_verification_study.py
#  \brief Python script for performing a verification study.
#  \author J. Mukhopadhaya

# imports
#import numpy as np
from optparse import OptionParser
import os, sys, shutil, copy, os.path
sys.path.append(os.environ['SU2_RUN'])
import SU2
from SU2.io import redirect_folder, redirect_output

def main():
# Command Line Options
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                      help="read config from FILE", metavar="FILE")

    (options, args)=parser.parse_args()

    # Config parsing
    config = SU2.io.Config(options.filename)
    state  = SU2.io.State()

    # Location to copy meshes from:
    mesh_loc = os.getcwd()
    mesh_files = [f for f in os.listdir(mesh_loc) if os.path.isfile(os.path.join(mesh_loc, f)) and f.endswith(".su2")]

    # copy mesh files
    #print('Copying mesh files to root folder... ')
    #for f in mesh_files:
    #    shutil.copy(os.path.join(mesh_loc,f),'.')
    #print('Copying complete')

    # folder set up
    mesh_folders = ['L5','L4','L3','L2','L1']
    models = ['SA']
    grads = {'gg' : 'GREEN_GAUSS'}
    recon_grads = ['']
    diverged_cases = []
    num_cores = {'L5': 1, 'L4' : 1, 'L3' : 4, 'L2' : 18, 'L1' : 18}

    for model in models:
        print('Running mesh convergence study for the ' + model + ' turbulence model: ')
        for grad_folder,grad in grads.items():
            print('\tUsing NUM_METHOD_GRAD = ' + grad)
            for recon in recon_grads:
                if recon:
                    print('\t\tUsing NUM_METHOD_GRAD_RECON = LEAST_SQUARES')
                else:
                    recon = '2nd_order'
                    print('\t\tUsing second order reconstructions')
                for level in mesh_folders:
                    curr_mesh = ''
                    for mesh in mesh_files:
                        if level in mesh:
                            curr_mesh = mesh
                            break
                    print('\t\t\tRunning ' + level + ' mesh level using ' + curr_mesh)
                    run_folder = '{}/{}/{}/{}/'.format(model,grad_folder,recon,level)

                    # make copies
                    konfig = copy.deepcopy(config)
                    ztate  = copy.deepcopy(state)

                    # update options
                    konfig.KIND_TURB_MODEL= model
                    konfig.NUM_METHOD_GRAD= grad
                    if 'ls' in recon:
                        konfig.NUM_METHOD_GRAD_RECON= 'LEAST_SQUARES'
                    konfig.MESH_FILENAME= curr_mesh
                    konfig.NUMBER_PART = num_cores[level]

                    ztate.find_files(konfig)

                    link = []
                    link.append(ztate.FILES['MESH'])

                    with redirect_folder(run_folder,[],link, force=False) as push:
                        with redirect_output('log.out'):
                            try:
                                print("running")
                                info = SU2.run.CFD(konfig)
                                ztate.update(info)
                            except:
                                print("The solver stopped unexpectedly")
                                diverged_cases.append(run_folder)
                                print("Continuing... ")

                    print("Following cases diverged: ")
                    print(diverged_cases)

if __name__ == "__main__":
    main()
