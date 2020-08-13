#!/usr/bin/env python3

"""Script to print the last value of all variables in a history file.

Author: Jayant Mukhopadhaya
Last updated: 08/12/2020"""

from io_su2.file_read_util import *
import numpy as np
import os
import sys

if len(sys.argv) == 1:
    filename = ''
    for file in os.listdir(os.getcwd()):
        if 'history' in file:
            filename = [file]
            break;
    assert filename, "No history file found"

else:
    filename = sys.argv[1:]
                
for name in filename:
    hist_data = read_history_data(name)
    for var,vec in hist_data.items():
        if not np.ndim(vec)==0:
            print(var + "= " + str(vec[-1]) + "\n")
        else:
            print(var + "= " + str(vec) + "\n")

