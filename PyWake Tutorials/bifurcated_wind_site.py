from py_wake.site import XRSite
from py_wake.site.shear import PowerShear
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from py_wake import NOJ
from my_site import wt_x, wt_y, MySite, V80
from py_wake.utils import weibull
from numpy import newaxis as na
from py_wake.wind_farm_models import All2AllIterative
# help call for info on the model
# help(All2AllIterative.__init__)

f = [0.5, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
A = [9.177, 9.782, 9.532, 9.91, 10.043, 9.594, 9.584, 10.515, 11.399, 11.687, 11.637, 10.088]
k = [2.393, 2.447, 2.412, 2.592, 2.756, 2.596, 2.584, 2.549, 2.471, 2.607, 2.627, 2.326]
wd = np.linspace(0, 360, len(f), endpoint=False)
ti = .1


# Site with wind direction dependent weibull distributed wind speed, constant turbulence intensity and power shear
my_site = XRSite(
    ds=xr.Dataset(data_vars={'Sector_frequency': ('wd', f), 'Weibull_A': ('wd', A), 'Weibull_k': ('wd', k), 'TI': ti},
                  coords={'i': [1, 2, 3, 4, 5], 'wd': wd}),
    shear=PowerShear(h_ref=100, alpha=.2))


# here we import the turbine, site and wake deficit model to use.
windTurbines = V80()
noj = NOJ(my_site, windTurbines)

# run the simulation for Annual Energy Production (AEP)
simulationResult = noj(wt_x, wt_y)
simulationResult.aep()
print("Total AEP: %f GWh" % simulationResult.aep().sum())

# plot the results
plt.figure()
aep = simulationResult.aep()
windTurbines.plot(wt_x, wt_y)
c = plt.scatter(wt_x, wt_y, c=aep.sum(['wd', 'ws']))
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
plt.figure()
flow_map.plot_wake_map()
plt.xlabel('x [m]')
plt.ylabel('y [m]')
plt.title('Wake map for' + f' {wind_speed} m/s and {wind_direction} deg')
plt.show()


