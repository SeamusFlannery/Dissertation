# Install PyWake
import py_wake
import numpy as np
import matplotlib.pyplot as plt
from py_wake.examples.data.hornsrev1 import Hornsrev1Site, V80, wt_x, wt_y, wt16_x, wt16_y
from py_wake import NOJ

# here we import the turbine, site and wake deficit model to use.
windTurbines = V80()
site = Hornsrev1Site()
noj = NOJ(site, windTurbines)

# run the simulation for Annual Energy Production (AEP)
simulationResult = noj(wt16_x, wt16_y)
simulationResult.aep()
print("Total AEP: %f GWh" % simulationResult.aep().sum())

# plot the results
plt.figure()
aep = simulationResult.aep()
windTurbines.plot(wt16_x, wt16_y)
c = plt.scatter(wt16_x, wt16_y, c=aep.sum(['wd', 'ws']))
plt.colorbar(c, label='AEP [GWh]')
plt.title('AEP of each turbine')
plt.xlabel('x [m]')
plt.ylabel('[m]')
plt.show()

plt.figure()
aep.sum(['wt', 'wd']).plot()
plt.xlabel("Wind speed [m/s]")
plt.ylabel("AEP [GWh]")
plt.title('AEP vs wind speed')
plt.show()

plt.figure()
aep.sum(['wt', 'ws']).plot()
plt.xlabel("Wind direction [deg]")
plt.ylabel("AEP [GWh]")
plt.title('AEP vs wind direction')
plt.show()

# Set a wind speed and direction to model wake in given scenario
wind_speed = 10
wind_direction = 200
# plot wake map
plt.figure()
flow_map = simulationResult.flow_map(ws=wind_speed, wd=wind_direction)
plt.figure(figsize=(18,10))
flow_map.plot_wake_map()
plt.xlabel('x [m]')
plt.ylabel('y [m]')
plt.title('Wake map for' + f' {wind_speed} m/s and {wind_direction} deg')
plt.show()