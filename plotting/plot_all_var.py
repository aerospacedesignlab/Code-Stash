#!/usr/bin/env python3

"""Script to plot all variables in a history file.
This script outputs .png files in a images sub-directory

Author: Jayant Mukhopadhaya
Last updated: 08/12/2020"""

from io_su2.file_read_util import *
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
if not os.path.isdir("images"):
    os.mkdir("images")

assert filename, "No history file found"
hist_data = read_history_data(filename)

for var,vec in hist_data.items():
    if 'history_project' in filename:
        plt.plot(hist_data["EVALUATION"],hist_data[var])
    elif "Iteration" in hist_data.keys():
        plt.plot(hist_data["Iteration"],hist_data[var])
    else:
        plt.plot(hist_data["Inner_Iter"],hist_data[var])
    plt.xlabel('Iteration')
    plt.ylabel(var)
    plt.tight_layout()
    plt.savefig("images/"+var.replace('/','_') + "_convergence.png")
    plt.clf()
plt.close()
