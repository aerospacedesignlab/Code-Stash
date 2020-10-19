from scipy.optimize import fsolve
from math import *
import numpy as np

def order_function(p,r32,r21,eps32,eps21):
    s = np.sign(eps32/eps21)
    q = log((r21**p-s)/(r32**p-s))
    return 1/log(r21)*(log(abs(eps32/eps21)+q)) - p

def numerical_discretization_error(h,phi,verbose=True):
    """Calculate numerical discretization error
    Keyword arguments:
    h -- tuple containing the three grid sizes h_i
    phi -- tuple containing corresponding solutions on each grid phi_i
    
    Return value:
    error -- dictionary containing error metrics
    
    Reference:  https://turbmodels.larc.nasa.gov/uncertainty_summary.pdf"""
    
    # Constants
    F_s = 1.25
    C_low = 0.95
    C_hi = 3.05
    delta_M = max(abs(phi[1]-phi[0]),abs(phi[2]-phi[1]),abs(phi[2]-phi[0]))
    
    # Mesh refinement ratios
    r21 = h[1]/h[0]
    r32 = h[2]/h[1]
    
    # Result ratios
    eps21 = phi[1] - phi[0]
    eps32 = phi[2] - phi[1]
    
    error = {}
    
    # Check for oscillatory convergence
    if eps32/eps21 < 0.0:
        if verbose:
            print("WARNING: Oscillatory convergence")
        error["Computed apparent order"] = 'NA'
        error["Relative fine-grid error"] = abs((phi[0]-phi[1])/phi[0])
        error["Extrapolated value"] = 'NA'
        error["Extrapolated relative fine-grid error"] = 'NA'
        error["Fine-grid convergence index"] = 'NA'
        error["Fine-grid convergence index, Corrected"] = 3.0*delta_M/abs(phi[0])
        error["Error Code"] = 1
        return error
    
    # Solve for apparent order
    p = fsolve(order_function,2,(r32,r21,eps32,eps21))
    p = p[0]
    
    # ASME Guidelines
    
    error["Computed apparent order"] = p
    error["Relative fine-grid error"] = abs((phi[0]-phi[1])/phi[0])
    error["Extrapolated value"] = (phi[0]*r21**p - phi[1])/(r21**p-1)
    error["Extrapolated relative fine-grid error"] = abs((error["Extrapolated value"]-phi[0])/error["Extrapolated value"])
    error["Fine-grid convergence index"] = F_s*error["Relative fine-grid error"]/(r21**p - 1)
    error["Error Code"] = 0
    
    # Extension to ASME Guidelines as presented in https://turbmodels.larc.nasa.gov/uncertainty_summary.pdf
    
    if p < 0.0:
        if verbose:
            print("WARNING: Negative apparent order")
        error["Fine-grid convergence index, Corrected"] = 3.0*delta_M/abs(phi[0])
        error["Error Code"] = 2
        
    if p < C_low and p > 0.0:
        if verbose:
            print("WARNING: Apparent order is less than " + str(C_low))
        error["Fine-grid convergence index, Corrected"] = min(error["Fine-grid convergence index"],F_s*delta_M/abs(phi[0]))
        error["Error Code"] = 3
    elif p > C_hi:
        if verbose:
            print("WARNING: Apparent order is greater than " + str(C_hi))
        error["Fine-grid convergence index, Corrected"] = min(F_s*error["Relative fine-grid error"]/(r21**C_hi - 1),F_s*delta_M/abs(phi[0]))
        error["Error Code"] = 4
        
    return error
