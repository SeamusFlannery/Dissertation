# Written by Seamus Flannery
# the goal of this file is to write an optimal shift lookup table for a given farm and site for every degree increment
# of incoming wind, so that a long simulation can quickly access the optimal shift position for the dynamic farm
# without recalculating the optimization curve and finding its maximum.
# even this could be further optimized: I could make it so that it only makes a table for the degrees that actually appear
# in the time series data (that didn't seem like a significant enough efficiency boost to my code to make it worth implementing)
from Stationholding import test_perp_slide
import numpy as np


# This method generates a lookup table given a site (generated from the time series data), farm, and turbine model.
def gen_lookup(site, farm, turbine, outname='farm_lookup'):
    dia = turbine.diameter()
    degrees = np.linspace(1, 360, 360)
    shift_table = np.empty(len(degrees))
    for i, degree in enumerate(degrees):
        print(f'Generating lookup table entry for {degree} degrees wind')
        shift_table[i] = test_perp_slide(site, farm, turbine, - dia * 3.3, dia * 3.3, granularity=dia * 0.1, wd=degree, plot=False)[1]
    output = np.array([degrees, shift_table]).T
    np.savetxt(outname, output, delimiter=',')
    return degrees, shift_table


# this method finds a given lookup table and returns the table as an array which can be used by a simulation to access
# shift values
def read_lookup(filename):
    file = np.loadtxt(filename, delimiter=',')
    degrees = file.T[0]
    shift_table = file.T[1]
    return degrees, shift_table
