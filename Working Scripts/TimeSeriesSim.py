import numpy as np
import datetime
import matplotlib.pyplot as plt
from py_wake.examples.data import example_data_path
from py_wake.wind_turbines.power_ct_functions import PowerCtFunctionList, PowerCtTabular
from py_wake.examples.data.hornsrev1 import Hornsrev1Site, V80
from py_wake.utils.plotting import setup_plot
from Stationholding import generate_layout, WindFarm, Turbine_instance
from sites import MyBiSite, MyTriSite, EastBlowHornsrevSite
from py_wake.wind_farm_models import PropagateDownwind
from py_wake import deficit_models as dm
import pandas as pd


def read_vortex(filepath: str) -> [list, list, int]:
    dates, times = np.loadtxt(filepath, delimiter=None, dtype=str, skiprows=4, usecols=[0, 1]).T
    ws, wd = np.loadtxt(filepath, delimiter=None, dtype=float, skiprows=4, usecols=[2, 3]).T
    timestamp = np.empty(dates.shape, dtype=datetime.datetime)
    for i, day in enumerate(dates):
        timestamp[i] = datetime.datetime.strptime(day[:4] + '/' + day[4:6] + '/' + day[6:8] + '/' + times[i][:2] + '/' + times[i][2:4], '%Y/%m/%d/%H/%M')
    return [ws, wd, timestamp]

def sim_time_series():

    sim_res_time = wf_model(farm_ex.wt_x, farm_ex.wt_y,  # wind turbine positions
                            wd=wd,  # Wind direction time series
                            ws=ws,  # Wind speed time series
                            time=time_stamp,  # time stamps
                            TI=ti,  # turbulence intensity time series
                            operating=operating  # time dependent operating variable
                            )


def main():
    ws, wd, times = read_vortex("WindData/Random/758955.6m_100m_UTC_04.0_ERA5.txt")
    print([times, ws, wd])


if __name__ == '__main__':
    main()