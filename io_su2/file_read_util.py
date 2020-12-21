import numpy as np
import os

def read_last_line(f):
    """Returns last line of file.
    
    Keyword arguments:
    f -- file object

    Return value:
    last -- string representing the last line in the file
    
    Author: https://stackoverflow.com/questions/3346430/what-is-the-most-efficient-way-to-get-first-and-last-line-of-a-text-file/3346788
    Last updated: 09/08/2020"""
    
    f.seek(-2, 2)              # Jump to the second last byte.
    while f.read(1) != b"\n":  # Until EOL is found ...
        f.seek(-2, 1)          # ... jump back, over the read byte plus one more.
    return f.read().decode('utf-8')            # Read all data from this point on.
    
def get_final_vals(filename = "history.csv"):
    """Returns last value of variables defined in the file
    
    Keyword arguments:
    filename -- Name of file from which variables and their last value needs to be extracted

    Return value:
    data_dict -- Dictionary where keys are variables names and values are their final values.
    
    Author: Jayant Mukhopadhaya
    Last updated: 09/08/2020"""
    
    file_name, file_extension = os.path.splitext(filename)
    
    # if tecplot file, use tecplot reader
    if file_extension == ".dat":
        with open(filename, "r") as f:
            line = f.readline()
            while line:
                if "variable" in line.lower():
                    line = line.split('=',1)[1]
                    if '\\' in line:
                        line = f.readline()
                        variables = [ var.strip().strip("\"") for var in line.split(",")]
                    else:
                        variables = [ var.strip().strip("\"") for var in line.split(",")]
                    break
        with open(filename,"rb") as f:
            vals = read_last_line(f)
            
        if ',' in vals:
            vals= [val.strip() for val in vals.split(',')]
        else:
            vals = vals.split()
    
    # if csv file, use csv reader
    elif file_extension == ".csv":
        with open(filename,"r") as fp:
            line = fp.readline()
            # Check for comments
            if '#' in line:
                line_parts = line.split('#')
                if not line_parts[0]:
                    line = fp.readline()
            # Read variable list
            else:
                variables = [i.strip().strip('\""') for i in line.split(",")]
        
        with open(filename,"rb") as f:
            vals = read_last_line(f)
        vals= [val.strip() for val in vals.split(',')]
    
    # invalid file extension
    else:
        print("This function can only read tabular tecplot or csv data")
        return 0
    
    data_dict = {}
    for i,var in enumerate(variables):
        data_dict[var] = float(vals[i])
    
    return data_dict     
    
def get_mesh_data(filename = 'mesh.su2', var = ''):
    """Goes through mesh file and can extract NELEM or NPOIN based on input var.
    
    Keyword arguments:
    filename -- name of mesh file.
    var -- variable that needs to be extracted from the mesh file.
           If nothing is specified, all data, except points and elements, is extracted
    
    Return value:
    N -- value of var from the mesh file specified by filename. 
    or 
    data -- dictionary that contains all the mesh data organized as: 

    data =  {   NDIME = ...,
                NELEM = ...,
                NPOIN = ...,
                NMARK = ...,
                MARKERS= { marker_name0 : marker_elem0,
                           marker_name1 : marker_elem1,
                           .
                           .
                        marker_nameN : marker_elemN}
            }
    
    Author: Jayant Mukhopadhaya
    Last updated: 08/12/2020"""
    keywords = ['NELEM', 'NPOIN','NDIME','NMARK','MARKER_TAG']
    N = 0
    data = {}
    with open(filename) as fp:
        # Read file line by line so that we can exit before reading the whole file
        line = fp.readline()

        # Reading all data from the mesh file
        if not var:
            while line:
                # If comment or not a named property, skip
                if line[0] == '%' or not '=' in line:
                    line=fp.readline()
                    continue
                split_text = line.split("=")
                word = split_text[0].strip()

                # Ensure word is in list of keywords
                if word in keywords:
                    # if not marker information, save info directly in dict
                    if not 'MARKER' in word:
                        data[word] = int(split_text[-1].strip())
                    # if marker information...
                    else:
                        # initialize marker data in dict
                        if not 'MARKERS' in data.keys():
                            data['MARKERS'] = {}
                        # add tag and elem data
                        if 'TAG' in word:
                            tag = split_text[-1].strip()
                            # elem data associated with current tag
                            while not 'MARKER_ELEMS' in line:
                                line = fp.readline()
                            split_text = line.split("=")
                            elems = int(split_text[-1].strip())
                            data['MARKERS'][tag] = elems

                line=fp.readline()
            return data

        # Reading only specified value 
        else:
            while line:
                # If comment or not a named property, skip
                if line[0] == '%' or not '=' in line:
                    line=fp.readline()
                    continue
                # If chosen variable, save value and break loop
                if line.split("=")[0] == var:
                    split_text = line.split("=")
                    N = int(split_text[-1].strip())
                    break
                line=fp.readline()

    if not var:
        return data
    else:
        return N

def get_force_data(filename = 'forces_breakdown.dat'):
    """Goes through force breakdown file to extract component force coefficient data
    Currently only extracts C_L and C_D data seperated into pressure and viscous parts
    
    Keyword arguments:
    filename -- Name of forces breakdown file. Default is forces_breakdown.dat
    
    Return value:
    force_dict -- Dictionary containing extracted force data 
    
    Author: Jayant Mukhopadhaya
    Last updated: 08/12/2020"""

    force_dict = {}
    with open(filename) as fp:
        line = fp.readline()
        while line:
            if "Total" in line.split(":")[0]:
                coeff = line.split(":")[0].split("Total ")[1]
                split_text = line.split("|")
                for chunk in split_text:
                    if "Total" in chunk:
                        force_dict[coeff] = float(chunk.strip().split()[-1])
                    elif "Pressure" in chunk:
                        force_dict[coeff + 'p'] = float(chunk.strip().split()[-1])
                    elif "Friction" in chunk:
                        force_dict[coeff + 'v'] = float(chunk.strip().split()[-1])
                if 'CFy' in line:
                    break
            line=fp.readline()

    return force_dict

def get_performance_data(filename = 'performance_data.dat'):
    """Returns performance metrics as a dictionary
    
    Keyword arguments:
    filename -- Name of performance data file. This needs to be created 
                from the output log. Usually it is the last 25 lines of 
                the output log.
    
    Return value:
    perf_dict -- Dictionary containing performance data 
    
    Author: Jayant Mukhopadhaya
    Last updated: 21/12/2020"""

    perf_dict = {}
    with open(filename) as fp:
        line = fp.readline()
        while line:
            if "|" in line:
                split_text = line.split("|")
                for chunk in split_text:
                    if not chunk.strip():
                        continue
                    var = chunk.split(":")[0].strip()
                    perf_dict[var] = float(chunk.strip().split()[-1])
                    
            line=fp.readline()
    return perf_dict

def read_history_data(filename=''):
    """Goes through a provided SU2 history file and sorts data into a dictionary
    
    Keyword arguments:
    filename -- Name of history file.
    
    Return value:
    data_dict -- Dictionary containing history data with variable names as keys and
                 a numpy array as its corresponding values 
    
    Author: Jayant Mukhopadhaya
    Last updated: 08/12/2020"""
    
    assert filename, "Please pass filename as an argument to the function"
    
    file_name, file_extension = os.path.splitext(filename)
    
    # if tecplot file, use tecplot reader
    if file_extension == ".dat":
        data_dict = tecplot_history_reader(filename)
        
        # for the history data, return dictionary corresponding to the first zone
        # data_dict = list(data.values())[0]
        return data_dict
    
    # if csv file, use csv reader
    elif file_extension == ".csv":
        data_dict = csv_reader(filename)
        return data_dict
    
    # invalid file extension
    else:
        print("This function can only read tabular tecplot or csv data")
        return 0
        
def csv_reader(filename=''):
    """Reads csv file and organizes data into a dictionary and numpy arrays
    
    Keyword arguments:
    filename -- Name of csv file.
    
    Return value:
    data_dict -- Dictionary containing csv data with variable names as keys, and
                 a numpy array containing the corresponding column of numbers as
                 the values. 
    
    Author: Jayant Mukhopadhaya
    Last updated: 08/12/2020"""
    data_dict = {}
    skip = 0
    with open(filename) as fp:
        line = fp.readline()
        # Check for comments
        if '#' in line:
            line_parts = line.split('#')
            if not line_parts[0]:
                skip += 1
                line = fp.readline()
        # Read variable list
        else:
            variables = [i.strip().strip('\""') for i in line.split(",")]
            skip+=1
            
    # load data into a numpy array
    hist_data = np.loadtxt(filename, delimiter=',',skiprows=skip, unpack=True)
    
    # organize the dictionary
    for i,variable in enumerate(variables):
        data_dict[variable] = hist_data[i]
    
    return data_dict
    
def tecplot_reader(filename=''):
    """ASCII Tecplot reader for multiple zones. Only deals with tabular data.
    Handles tecplot files with multiple zones of tabular data.
    
    Keyword arguments:
    filename -- Name of tecplot file.
    
    Return value:
    data -- Dictionary containing extracted data. Organized as:
    data =  {{ ZONE_NAME_0 : 
                { VAR0 : numpy array containing data VAR0 data for ZONE0},
                { VAR1 : ...},
                {...}, 
                { VARN : ...}},
             .
             .
             .
             { ZONE_NAME_N : 
                { VAR0 : numpy array containing data VAR0 data for ZONE1},
                { VAR1 : ...},
                {...}, 
                { VARN : ...}}}
    
    Useful to read V&V files from the NASA TMR website.
    
    Author: Jayant Mukhopadhaya
    Last updated: 08/12/2020"""
    
    assert filename, "Please pass filename as an argument to the function"

    data = {}
    with open(filename, 'r') as a:
        variables = []
        lines = a.readlines()
        for idx, line in enumerate(lines):
            
            # Ignore any comment line
            if "#" in line:
                line = line.split("#")[0]
                if not line:
                    continue
                    
            # skip title line if there is one
            elif "title" in line.lower():
                continue
            
            # If its a list of variables, read the list
            elif "variable" in line.lower():
                line = line.split('=',1)[1]
                if '\\' in line:
                    line = lines[idx+1]
                variables = [ var.strip().strip("\"") for var in line.split(",")]
                continue
            
            # Check to see if there is a new zone definition
            elif "zone" in line.lower():
                # extract zone name
                zone_name = line.split("=",1)[1].strip()
                zone_name = zone_name.strip("\"")
                data[zone_name] = {}
                
                # if variable names are defined, assign an empty numpy array to that variable
                if variables:
                    for var in variables:
                        data[zone_name][var] = np.empty(0)
                continue
            
            # Sort data out into the different variables
            else:
                if '"' in line:
                    continue
                # if there is no zone defined, create a dummy zone named ZONE0
                if not 'zone_name' in locals():
                    zone_name = 'ZONE0'
                    data[zone_name] = {}
                
                    # if variable names are defined, assign an empty numpy array to that variable
                    if variables:
                        for var in variables:
                            data[zone_name][var] = np.empty(0)

                # if comma-delimited, seperate accordingly
                if ',' in line:
                    line_list= [val.strip() for val in line.split(',')]
                
                # else this is space-delimited
                else: 
                    line_list = line.split()
                
                for i,val in enumerate(line_list):
                    if variables:
                        data[zone_name][variables[i]] = np.append(data[zone_name][variables[i]],float(val))
                    
                    # if there aren't any variables defined, name them var# according to order of appearance
                    else:
                        if not data[zone_name]:
                            for j in range(0,len(line.split())):
                                data[zone_name]['var'+str(j)] = np.empty(0)
                        data[zone_name]['var'+str(i)] = np.append(data[zone_name]['var'+str(i)],float(val))
    return data

def tecplot_history_reader(filename=''):
    """ASCII Tecplot reader for multiple zones. Only deals with tabular data.
    Handles tecplot files with multiple zones of tabular data.
    
    Keyword arguments:
    filename -- Name of tecplot file.
    
    Return value:
    data -- Dictionary containing extracted data. Organized as:
    data =  {{ ZONE_NAME_0 : 
                { VAR0 : numpy array containing data VAR0 data for ZONE0},
                { VAR1 : ...},
                {...}, 
                { VARN : ...}},
             .
             .
             .
             { ZONE_NAME_N : 
                { VAR0 : numpy array containing data VAR0 data for ZONE1},
                { VAR1 : ...},
                {...}, 
                { VARN : ...}}}
    
    Useful to read V&V files from the NASA TMR website.
    
    Author: Jayant Mukhopadhaya
    Last updated: 08/12/2020"""
    
    assert filename, "Please pass filename as an argument to the function"

    data_dict = {}
    with open(filename, 'r') as a:
        variables = []
        line = a.readline()
        line = a.readline()
        variables = [ var.strip().strip("\"") for var in line.split(",")]
    # load data into a numpy array
    hist_data = np.loadtxt(filename, delimiter=',',skiprows=2, unpack=True)
    
    # organize the dictionary
    for i,variable in enumerate(variables):
        data_dict[variable] = hist_data[i]
    
    return data_dict

def read_constraints(filename='config.cfg'):
    """Goes through a provided SU2 configuration file and extracts constraint data
    
    Keyword arguments:
    filename -- Name of config file.
    
    Return value:
    constraint_dict -- Dictionary containing constraint data with data organized as: 
    constraint_dict =  {{ CONSTRAINT_NAME_0 : 
                            { Value : Numerical value},
                            { Sign  : Sign as a string},
                            { Scale : Numerical value}}, 
                        .
                        .
                        .
                        { CONSTRAINT_NAME_N : 
                            { Value : Numerical value},
                            { Sign  : Sign as a string},
                            { Scale : Numerical value}}}
    
    Author: Jayant Mukhopadhaya
    Last updated: 08/12/2020"""
    
    constraint_dict = {}
    with open(filename) as fp:
        line = fp.readline()
        while line:
        
            # find line defining constraints
            if "OPT_CONSTRAINT" in line and not line.startswith('%'):
                const_string = line.split("=",1)[1]
                
                # for each constraint
                for constraint_scale in const_string.split(';'):
                    constraint = constraint_scale.split('*')[0]
                    
                    # split along sign
                    for this_sgn in ['<','>','=']:
                        if this_sgn in constraint: break
                    obj_val = constraint.strip(' () ').split(this_sgn)
                    assert len(obj_val) == 2 , 'incorrect constraint definition'
                    
                    # extract numerical value of constraint
                    obj = obj_val[0].strip()
                    val = float( obj_val[1] )
                    
                    # save data in the dictionary
                    constraint_dict[obj] = {}
                    constraint_dict[obj]["Value"] = val
                    constraint_dict[obj]["Sign"]  = this_sgn
                    constraint_dict[obj]["Scale"] = float(constraint_scale.split('*')[1].strip())
                break;                
            line=fp.readline()
    return constraint_dict

def geo_locations(filename='config.cfg'):
    """Goes through a provided SU2 configuration file and extracts geometry evaluation locations
    
    Keyword arguments:
    filename -- Name of config file.
    
    Return value:
    geo_dict -- Dictionary containing geometry evaluation data with geometry type as the key, 
                and numpy array containing the corresponding locations as the value  
    
    Author: Jayant Mukhopadhaya
    Last updated: 08/12/2020"""
    
    geo_dict = {}
    with open(filename) as fp:
        line = fp.readline()
        while line:
        
            # find line with geometry descriptions and split into a list
            if "GEO_DESCRIPTION" in line and not line.startswith('%'):
                geo_string = line.split("=",1)[1]
                geo_list = [i.strip() for i in geo_string.split(";")]
            
            # find line with geometry locations and split into numpy arrays
            elif "GEO_LOCATION" in line and not line.startswith('%'):
                geo_string = line.split("=",1)[1]
                geo_loc_list = []
                for geo_loc in geo_string.split(";"):
                    geo_loc = geo_loc.strip().strip('()')
                    geo_loc = np.asarray([float(num.strip()) for num in geo_loc.split(',')])
                    geo_loc_list.append(geo_loc)                
            line=fp.readline()

    assert len(geo_loc_list) == len(geo_list) , 'inconsistent definitions of GEO_LOCATION_STATIONS and \
                                                GEO_DESCRIPTION. Both must have the same number of elements'
    # organize data in dictionary
    for i,geo_type in enumerate(geo_list):
        geo_dict[geo_type] = geo_loc_list[i]

    return geo_dict
    
def organize_airfoil_data(x,z):
    """Organizes input airfoil coordinates into upper and lower surfaces
    
    Keyword arguments:
    x -- x-coordinates of airfoil (in the chord-wise direction)
    z -- z-coordinates of airfoil (in the thickness direction)
    
    Return value:
    lower -- numpy array  containing lower surface coordinates using custom dtypes
             Keys are 'x' and 'z'
    upper -- numpy array  containing upper surface coordinates using custom dtypes
             Keys are 'x' and 'z'
             
    This is not a perfect script. It uses a simple heuristic to sort the data into
    upper and lower surfaces:
    1) The coordinates are sorted using x-coordinates
    2) Initial upper and lower surfaces are sorted using the first z value. If a 
       coordinate is > z[0] then it goes into the upper surface, and vice-versa
    3) The surface with more points is iterated through. Distance of each point
       is checked against the last point in the upper and lower surface arrays.
       If the point is closer to the last point in the lower surface, the point is
       moved to the lower surface array. 
 
    Author: Jayant Mukhopadhaya
    Last updated: 08/12/2020"""
    
    # create numpy array with custom dtypes
    coords= np.zeros(x.size, dtype={'names':('x', 'z'),
                          'formats':(x.dtype,z.dtype)})
    coords['x'] = x
    coords['z'] = z
    
    # sort according to x coordinate
    coords=np.sort(coords,order='x')
    
    # split coordinates into upper and lower arrays according to the first z-coordinate
    upper = coords[coords['z'] >= coords['z'][0]]
    lower = coords[coords['z'] < coords['z'][0]]

    inds_to_delete = np.array([],dtype=np.int16)
    last_ind = 0
    
    # determine which surface has more points that might need to be moved to other surface
    if upper['x'][-1] < lower['x'][-1]:
    
        # lower surface has more points, so iterate through each of those coordinates
        for i,coord in enumerate(lower):
        
            # determine last points in the sorted surfaces
            last_upper = upper[-1]
            last_lower = lower[last_ind]
            
            # if the current coordinate is further past the last sorted upper point, find distances
            if coord['x'] >= last_upper['x']:
                dist_to_lower = pow(pow(coord['x'] - last_lower['x'],2) + pow(coord['z'] - last_lower['z'],2),.5)
                dist_to_upper = pow(pow(coord['x'] - last_upper['x'],2) + pow(coord['z'] - last_upper['z'],2),.5)
                dist_to_lower = abs(coord['z'] - last_lower['z'])
                dist_to_upper = abs(coord['z'] - last_upper['z'])
                
                # if point is closer to the upper surface, append it to the upper array
                if dist_to_upper < dist_to_lower:
                    upper = np.append(upper, coord)
                    inds_to_delete = np.append(inds_to_delete,i)
                    
                # if closer to lower surface, update last_ind for sorted lower surface
                else:
                    last_ind = i    
            else:
                last_ind = i
                
        # purge any coordinates that were moved
        lower = np.delete(lower,inds_to_delete)

    else:
    
        # upper surface has more points, so iterate through each of those coordinates
        for i,coord in enumerate(upper):
        
            # determine last points in the sorted surfaces
            last_lower = lower[-1]
            last_upper = upper[last_ind]
            
            # if the current coordinate is further past the last sorted lower point, find distances
            if coord['x'] >= last_lower['x']:
                dist_to_lower = pow(pow(coord['x'] - last_lower['x'],2) + pow(coord['z'] - last_lower['z'],2),.5)
                dist_to_upper = pow(pow(coord['x'] - last_upper['x'],2) + pow(coord['z'] - last_upper['z'],2),.5)
                dist_to_lower = abs(coord['z'] - last_lower['z'])
                dist_to_upper = abs(coord['z'] - last_upper['z'])

                # if point is closer to the lower surface, append it to the lower array
                if dist_to_lower < dist_to_upper:
                    lower = np.append(lower, coord)
                    inds_to_delete = np.append(inds_to_delete,i)
                
                # if closer to upper surface, update last_ind for sorted upper surface
                else:
                    last_ind = i    
            else:
                last_ind = i
        
        # purge any coordinates that were moved
        upper = np.delete(upper,inds_to_delete)

    return upper,lower
