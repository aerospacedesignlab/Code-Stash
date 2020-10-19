#!/usr/bin/env python

## \file run_verification_study.py
#  \brief Python script for performing a verification study.
#  \author J. Mukhopadhaya
#
#  This script runs a set of simulations for a verification study.
#  It requires a config file as a command line input.
#  It uses all the mesh files found in the working directory as a mesh
#  family. Mesh files should have the level (L5, L4, ... etc) in its
#  name.
# 
#  Currently, this verfication study runs SA, and SST turbulence models
#  with the GG, and WLSQ numerical gradient methods, and with Least
#  Squares, and 2nd order flux reconstructions. This can be changed by
#  altering the options in the run set up section.


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
    
    # Assumption: All .su2 meshes in family are present in current directory
    files = [f for f in os.listdir(os.getcwd()) if os.path.isfile(os.path.join(os.getcwd(), f))]
    mesh_files = [f for f in files if '.su2' in f]

    # Run set up
    mesh_folders = ['L5','L4','L3','L2','L1']
    models = ['SA', 'SST']
    grads = {'gg' : 'GREEN_GAUSS', 'wlsq' : 'WEIGHTED_LEAST_SQUARES'}
    recon_grads = ['ls','2nd_order']
    diverged_cases = []
    num_cores = {'L5': 1, 'L4' : 2, 'L3' : 8, 'L2' : 32, 'L1' : 128}

    for model in models:
        print('Running mesh convergence study for the ' + model + ' turbulence model: ')
        for grad_folder,grad in grads.items():
            print('\tUsing NUM_METHOD_GRAD = ' + grad)
            for recon in recon_grads:
                if 'ls' in recon:
                    print('\t\tUsing NUM_METHOD_GRAD_RECON = LEAST_SQUARES')
                else:
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
