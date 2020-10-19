import numpy as np
from paraview.simple import *

def extract_variable_at_point(fn='',x=0.0,y=0.0,z=0.0,var='',eps=1e-5):
    reader = XMLUnstructuredGridReader(FileName=fn)
    assert var in reader.PointArrayStatus, 'Invalid variable name, variables in file are: ' + reader.PointArrayStatus
    data = servermanager.Fetch(reader)
    var_array = data.GetPointData().GetAbstractArray(var)
    nP = data.GetNumberOfPoints()
    index = 0
    for i in range(nP):
        coords = data.GetPoint(i)
        dx = abs(x-coords[0])
        dy = abs(y-coords[1])
        dz = abs(z-coords[2])
        if dx < eps and dy < eps and dz < eps:
            index = i
            break
    extracted_data = []
    for i in range(var_array.GetNumberOfComponents()):
        extracted_data.append(var_array.GetComponent(index,i))
    return np.array(extracted_data)