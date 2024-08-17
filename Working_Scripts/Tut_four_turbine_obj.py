# a tutorial file I worked in provided by the PyWake developers in the documentation
import numpy as np
import matplotlib.pyplot as plt
from py_wake.wind_turbines import WindTurbine, WindTurbines
from py_wake.examples.data.hornsrev1 import V80
from py_wake.examples.data.iea37 import IEA37_WindTurbines, IEA37Site
from py_wake.examples.data.dtu10mw import DTU10MW

v80 = V80()
iea37 = IEA37_WindTurbines()
dtu10mw = DTU10MW()
# can also import from WAsP.wtg files


# self-defined turbine (or use GenericWindTurbine class):
from py_wake.wind_turbines.power_ct_functions import PowerCtTabular

u = [0, 3, 12, 25, 30]
ct = [0, 8 / 9, 8 / 9, .3, 0]
power = [0, 0, 2000, 2000, 0]

my_wt = WindTurbine(name='MyWT',
                    diameter=123,
                    hub_height=321,
                    powerCtFunction=PowerCtTabular(u, power, 'kW', ct))

# GenericWindTUrbine example:
from py_wake.wind_turbines.generic_wind_turbines import GenericWindTurbine

# for a diameter of 178.3m and hub height of 119m
gen_wt = GenericWindTurbine('G10MW', 178.3, 119, power_norm=10000, turbulence_intensity=.1)

# You can collect a list of different turbine types into a single WindTurbines object
wts = WindTurbines.from_WindTurbine_lst([v80, iea37, dtu10mw, my_wt, gen_wt])
types = wts.types()
print("Name:\t\t%s" % "\t".join(wts.name(types)))
print('Diameter[m]\t%s' % "\t".join(map(str, wts.diameter(type=types))))
print('Hubheigt[m]\t%s' % "\t".join(map(str, wts.hub_height(type=types))))

# plot power curves
ws = np.arange(3, 25)
plt.xlabel('Wind speed [m/s]')
plt.ylabel('Power [kW]')

for t in types:
    plt.plot(ws, wts.power(ws, type=t) * 1e-3, '.-', label=wts.name(t))
plt.legend(loc=1)
plt.show()

# plot Ct curves:
plt.xlabel('Wind speed [m/s]')
plt.ylabel('CT [-]')

for t in types:
    plt.plot(ws, wts.ct(ws, type=t), '.-', label=wts.name(t))
plt.legend(loc=1)
plt.show()

# Wind Turbines can be passed as an xarray dataset:
# import xarray as xr
# from py_wake.wind_turbines.power_ct_functions import PowerCtXr

# ds = xr.Dataset(
#     data_vars={'power': (['ws', 'rho'], np.array([p1, p0]).T),
#                'ct': (['ws', 'boost'], np.array([ct1, ct0]).T)},
#     coords={'rho': [0.95, 1.225], 'ws': ws})

# curve = PowerCtXr(ds, 'w')

# specifying a diameter of 112m and hub height of 84m
# wt = WindTurbine('AirDensityDependentWT', 112, 84, powerCtFunction=powerCtFunction)
#
# # looping through different values of air density
# for r in [0.995, 1.1, 1.225]:
#     plt.plot(wt.power(ws, rho=r) / 1000, label=f'Air density: {r}')
# plt.ylabel('Power [kW]')
# plt.xlabel('Wind speed [m/s]')
# plt.legend()
# plt.show()

# plot variety of wind turbines:
s = IEA37Site(16)
x, y = s.initial_position.T

plt.figure()
wts.plot_xy(x, y, types=np.arange(len(x)) % len(types))
plt.xlim(-2000, 2000)
plt.xlabel('x [m]')
plt.ylabel('y [m]')
plt.legend()
plt.show()

# here you can also specify yaw angles for the turbines
plt.figure()
wts.plot_yz(np.array([-600,0,600]), wd=0, types=[0,1,2], yaw=[-30, 10, 90])
plt.ylim(-400,400)
plt.xlim(-800,800)
plt.xlabel('y [m]')
plt.ylabel('z [m]')
plt.legend()
plt.show()