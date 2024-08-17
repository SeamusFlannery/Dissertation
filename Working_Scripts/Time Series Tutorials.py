# this file written by PyWake devs and then copied and maybe editted by Seamus Flannery while trying to
# learn how to use PyWake.
# load a time series of wd, ws and ti
import numpy as np
import matplotlib.pyplot as plt
from py_wake.examples.data import example_data_path
from py_wake.wind_turbines.power_ct_functions import PowerCtFunctionList, PowerCtTabular
from py_wake.examples.data.hornsrev1 import Hornsrev1Site, V80
from py_wake.utils.plotting import setup_plot
from Stationholding import generate_layout, WindFarm, Turbine_instance
from sites import MyBiSite, MyTriSite, EastBlowHornsrevSite
from py_wake.wind_farm_models import PropagateDownwind
from py_wake import deficit_models as dm

windTurbines = V80()

d = np.load(example_data_path + "/time_series.npz")
n_days = 30
wd, ws, ws_std = [d[k][:6 * 24 * n_days] for k in ['wd', 'ws', 'ws_std']]
ti = np.minimum(ws_std / ws, .5)
time_stamp = np.arange(len(wd)) / 6 / 24

# plot time series
axes = plt.subplots(3, 1, sharex=True, figsize=(16, 10))[1]

for ax, (v, l) in zip(axes, [(wd, 'Wind direction [deg]'), (ws, 'Wind speed [m/s]'), (ti, 'Turbulence intensity')]):
    ax.plot(time_stamp, v)
    ax.set_ylabel(l)
_ = ax.set_xlabel('Time [day]')

# replace powerCtFunction
windTurbines.powerCtFunction = PowerCtFunctionList(
    key='operating',
    powerCtFunction_lst=[PowerCtTabular(ws=[0, 100], power=[0, 0], power_unit='w', ct=[0, 0]),  # 0=No power and ct
                         V80().powerCtFunction],  # 1=Normal operation
    default_value=1)

# plot power curves
u = np.arange(3, 26)
for op in [0, 1]:
    plt.plot(u, windTurbines.power(u, operating=op) / 1000, label=f'Operating={op}')
setup_plot(xlabel='Wind speed [m/s]', ylabel='Power [kW]')
# plt.show()
farm_ex = WindFarm(generate_layout(10, 500, 10, 500, 0))
# Make time-dependent operating variable
operating = np.ones((len(farm_ex.turbines), len(time_stamp)))  # shape=(#wt, #time stamps)
operating[0, (time_stamp > 15) & (time_stamp < 20)] = 0  # wt0 not operating from day 5 to 15

# setup new WindFarmModel with site containing time-dependent TI and run simulation
wf_model = PropagateDownwind(MyBiSite(), windTurbines, wake_deficitModel=dm.NOJDeficit())

sim_res_time = wf_model(farm_ex.wt_x, farm_ex.wt_y,  # wind turbine positions
                        wd=wd,  # Wind direction time series
                        ws=ws,  # Wind speed time series
                        time=time_stamp,  # time stamps
                        TI=ti,  # turbulence intensity time series
                        operating=operating  # time dependent operating variable
                        )
print(float(sim_res_time.aep().sum()))



