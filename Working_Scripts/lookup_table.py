# the goal of this file is to write an optimal shift lookup table for a given farm and site
from Stationholding import test_perp_slide
import numpy as np


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


def read_lookup(filename):
    file = np.loadtxt(filename, delimiter=',')
    degrees = file.T[0]
    shift_table= file.T[1]
    return degrees, shift_table
