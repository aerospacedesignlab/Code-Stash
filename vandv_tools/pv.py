import numpy as np
from paraview.simple import *

class PVWrapper:

    def __init__(self,filename=''):
        self.filename = filename
        self.reader = XMLUnstructuredGridReader(FileName=filename)
        self.variables = self.reader.PointArrayStatus
        self.data = servermanager.Fetch(self.reader)



    def extract_variables_at_loc(self,loc=(0.0,0.0,0.0), eps=1e-5):
        """Extract all variables at location specified
        Keyword arguments:
        loc -- tuple containing the (x,y,z) coordinates of location 
               (default (0.0,0.0,0.0))
        eps -- tolerance for coordinate comparison (default 1e-5)

        Return value: 
        Dictionary where the keys are variable names and the values are
        the value of that variable at location specified by loc

        """
        nP = self.data.GetNumberOfPoints()
        index = 0
        for i in range(nP):
            coords = self.data.GetPoint(i)
            dx = abs(loc[0]-coords[0])
            dy = abs(loc[1]-coords[1])
            dz = abs(loc[2]-coords[2])
            if dx < eps and dy < eps and dz < eps:
                index = i
                break
        
        return self.extract_variables_at_index(idx=index)

    def extract_variables_along_axis(self,loc=(0.0,0.0),axis='y', eps=1e-5):
        """Extract all variables along axis at location specified
        Keyword arguments:
        loc -- tuple containing the 2 coordinates defining the axis
               location (default (0.0,0.0))
        axis -- string defining axis direction
        eps -- tolerance for coordinate comparison (default 1e-5)

        Return value: 
        Dictionary where the keys are variable names and the values are
        the value of that variable at location specified by loc

        """

        if axis == 'x':
            indx = 1
            indy = 2
        elif axis == 'y':
            indx = 0
            indy = 2
        elif axis == 'z':
            indx = 0
            indy = 1


        nP = self.data.GetNumberOfPoints()
        inds = []
        for i in range(nP):
            coords = self.data.GetPoint(i)
            dx = abs(loc[0]-coords[indx])
            dy = abs(loc[1]-coords[indy])
            if dx < eps and dy < eps:
                inds.append(i)
        
        return self.extract_variables_at_index(idx=inds)

    def extract_variables_at_index(self,idx=0, eps=1e-5):
        data_dict = {}
        if isinstance(idx,list):
            n_ind = len(idx)
            data_dict['X'] = np.empty(n_ind)
            data_dict['Y'] = np.empty(n_ind)
            data_dict['Z'] = np.empty(n_ind)
            for var in self.variables:
                var_array = self.data.GetPointData().GetAbstractArray(var)
                data_dict[var] = np.empty((n_ind,var_array.GetNumberOfComponents()))
                for i,ind in enumerate(idx):
                    data_dict['X'][i] = self.data.GetPoint(ind)[0]
                    data_dict['Y'][i] = self.data.GetPoint(ind)[1]
                    data_dict['Z'][i] = self.data.GetPoint(ind)[2]
                    if var_array.GetNumberOfComponents() > 1:
                        for j in range(var_array.GetNumberOfComponents()):
                            data_dict[var][i,j] = var_array.GetComponent(ind,j)
                    else:
                        data_dict[var][i] = var_array.GetComponent(ind,0)
        else:

            for var in self.variables:
                var_array = self.data.GetPointData().GetAbstractArray(var)
                if var_array.GetNumberOfComponents() > 1:
                    extracted_data = []
                    for i in range(var_array.GetNumberOfComponents()):
                        extracted_data.append(var_array.GetComponent(idx,i))
                    data_dict[var] = extracted_data
                else:
                    data_dict[var] = var_array.GetComponent(idx,0)
        
        return data_dict