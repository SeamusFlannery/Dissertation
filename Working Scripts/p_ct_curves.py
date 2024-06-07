# Using this document to store the data arrays for my power curves and ct_curves
import numpy as np

V80power_curve = np.array(
    [[3.0, 0.0], [4.0, 66.6], [5.0, 154.0], [6.0, 282.0], [7.0, 460.0], [8.0, 696.0], [9.0, 996.0], [10.0, 1341.0],
     [11.0, 1661.0], [12.0, 1866.0], [13.0, 1958.0], [14.0, 1988.0], [15.0, 1997.0], [16.0, 1999.0], [17.0, 2000.0],
     [18.0, 2000.0], [19.0, 2000.0], [20.0, 2000.0], [21.0, 2000.0], [22.0, 2000.0], [23.0, 2000.0], [24.0, 2000.0],
     [25.0, 2000.0]]) * [1, 1000]

V80ct_curve = np.array(
    [[3.0, 0.0], [4.0, 0.818], [5.0, 0.806], [6.0, 0.804], [7.0, 0.805], [8.0, 0.806], [9.0, 0.807], [10.0, 0.793],
     [11.0, 0.739], [12.0, 0.709], [13.0, 0.409], [14.0, 0.314], [15.0, 0.249], [16.0, 0.202], [17.0, 0.167],
     [18.0, 0.14], [19.0, 0.119], [20.0, 0.102], [21.0, 0.088], [22.0, 0.077], [23.0, 0.067], [24.0, 0.06],
     [25.0, 0.053]])

# “turbine-models/Offshore/IEA_15MW_240_RWT.csv at master · NREL/turbine-models,” GitHub. Accessed: Jun. 07, 2024. [Online]. Available: https://github.com/NREL/turbine-models/blob/master/Offshore/IEA_15MW_240_RWT.csv
NREL15power_curve = np.loadtxt("IEA_15MW_240_RWT.csv", delimiter=',', skiprows=1, usecols=[0,1])
NREL15ct_curve = np.loadtxt("IEA_15MW_240_RWT.csv", delimiter=',', skiprows=1, usecols=[0,4])

