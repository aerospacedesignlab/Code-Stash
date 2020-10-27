import numpy as np
import os
from io_su2.file_read_util import *

def get_mesh_names(path = '', extension = '.su2'):
    """Returns names of mesh files in path with given extension
    
    Keyword arguments:
    path -- Path to folder where mesh files are located
    extension -- extension of the mesh files to look for

    Return value:
    mesh_names -- list containing mesh file names 
    
    Author: Jayant Mukhopadhaya
    Last updated: 10/13/2020"""

    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    mesh_files = [f for f in files if extension in f]
    return mesh_files

def get_mesh_family_data(meshes, var = 'NPOIN'):
    ndim = get_mesh_data(meshes[0])['NDIME']
    mesh_data = {'N' : [] , 'h' : []}
    for mesh in meshes:
        mesh_data['N'].append(get_mesh_data(mesh,var))
    mesh_data['N'].sort()
    mesh_data['h'] = [(1/i)**(1/ndim) for i in mesh_data['N']]
    return mesh_data

def calculate_uplus_yplus(y,rho,vel_u,mu):
    inds = np.argsort(y)
    y = y[inds]
    rho= rho[inds]
    vel_u = vel_u[inds]
    mu = mu[inds]
    nu = np.divide(mu,rho)
    tau_wall = mu[0] * (vel_u[1] - vel_u[0])/(y[1] - y[0])
    utau = np.sqrt(tau_wall/rho[0])
    uplus = vel_u / utau
    yplus = y * np.divide(utau,nu)
    return uplus,yplus