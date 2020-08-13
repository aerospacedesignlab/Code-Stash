#!/usr/bin/env python3

"""Script to plot convergence history and output a .png file.
Only plots Density residual against iteration

Author: Jayant Mukhopadhaya
Last updated: 08/12/2020"""

from su2_io.file_read_util import *
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import os

textFontSize = 16
tickFontSize = 14
matplotlib.rc('font', size=tickFontSize)

filename = ''
for file in os.listdir(os.getcwd()):
    if 'history' in file:
        filename = file

assert filename, "No history file found"
hist_data = read_history_data(filename)

if "Iteration" in hist_data.keys():
    plt.plot(hist_data["Iteration"],hist_data["Res_Flow[0]"])
    plt.xlabel('Iteration')
    plt.ylabel('rms[Rho]')
    plt.tight_layout()

else:
    for var,vec in hist_data.items():
        if "[Rho]" in var or "[A_Rho]" in var:
            plt.plot(hist_data["Inner_Iter"],hist_data[var])
            plt.xlabel('Iteration')
            plt.ylabel(var)
            plt.tight_layout()
            break

plt.savefig("convergence.png")
plt.close()
