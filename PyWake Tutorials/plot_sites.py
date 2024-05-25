from py_wake.site import XRSite
from py_wake.site.shear import PowerShear
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from py_wake import NOJ
from my_site import MySite, V80, simple_farm
from North_Wind import NorthMySite
from py_wake.utils import weibull
from numpy import newaxis as na
from py_wake.wind_farm_models import All2AllIterative
from py_wake import deficit_models as dm
# help call for info on the model
# help(All2AllIterative.__init__)

# here we import the turbine, site and wake deficit model to use.
windTurbines = V80()
Sim = All2AllIterative(MySite(), windTurbines, wake_deficitModel=dm.NOJDeficit())
wt_x, wt_y = simple_farm.wt_x, simple_farm.wt_y
# run the simulation for Annual Energy Production (AEP)
simulationResult = Sim(wt_x, wt_y)
AEP = simulationResult.aep(normalize_probabilities=True)
print("Total AEP: %f GWh" % AEP.sum())


# plot the results
# plt.figure()
# aep = simulationResult.aep()
# windTurbines.plot(wt_x, wt_y)
# c = plt.scatter(wt_x, wt_y, c=aep.sum(['wd', 'ws']))
# plt.colorbar(c, label='AEP [GWh]')
# plt.title('AEP of each turbine')
# plt.xlabel('x [m]')
# plt.ylabel('[m]')
# plt.show()

# plt.figure()
# aep.sum(['wt', 'wd']).plot()
# plt.xlabel("Wind speed [m/s]")
# plt.ylabel("AEP [GWh]")
# plt.title('AEP vs wind speed')
# plt.show()
#
# plt.figure()
# aep.sum(['wt', 'ws']).plot()
# plt.xlabel("Wind direction [deg]")
# plt.ylabel("AEP [GWh]")
# plt.title('AEP vs wind direction')
# plt.show()

# Set a wind speed and direction to model wake in given scenario
wind_speed = 10
wind_direction = 200
# plot wake map
plt.figure()
flow_map = simulationResult.flow_map(ws=wind_speed, wd=wind_direction)
plt.figure()
flow_map.plot_wake_map()
plt.xlabel('x [m]')
plt.ylabel('y [m]')
plt.title('Wake map for' + f' {wind_speed} m/s and {wind_direction} deg')
plt.show()


windTurbines = V80()
Sim2 = All2AllIterative(NorthMySite(), windTurbines, wake_deficitModel=dm.NOJDeficit())
simulationResult2 = Sim2(wt_x, wt_y)
AEP2 = simulationResult2.aep(normalize_probabilities=True)
print("Total AEP: %f GWh" % AEP2.sum())
wind_speed = 10
wind_direction = 0
# plot wake map
plt.figure()
flow_map2 = simulationResult2.flow_map(ws=wind_speed, wd=wind_direction)
plt.figure()
flow_map.plot_wake_map()
plt.xlabel('x [m]')
plt.ylabel('y [m]')
plt.title('Wake map for' + f' {wind_speed} m/s and {wind_direction} deg')
plt.show()