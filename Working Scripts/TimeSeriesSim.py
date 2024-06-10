import numpy as np
import datetime
import matplotlib.pyplot as plt
from py_wake.examples.data import example_data_path
from py_wake.wind_turbines.power_ct_functions import PowerCtFunctionList, PowerCtTabular
from py_wake.examples.data.hornsrev1 import Hornsrev1Site, V80
from py_wake.utils.plotting import setup_plot
from Stationholding import generate_layout, WindFarm, Turbine_instance
from turbines import NREL15
from sites import MyBiSite, MyTriSite, EastBlowHornsrevSite, SiteFromSeries
from py_wake.wind_farm_models import PropagateDownwind
from py_wake import deficit_models as dm
import scipy as sp
import pandas as pd


def read_vortex(filepath: str) -> [list, list, int]:
    dates, times = np.loadtxt(filepath, delimiter=None, dtype=str, skiprows=4, usecols=[0, 1]).T
    ws, wd = np.loadtxt(filepath, delimiter=None, dtype=float, skiprows=4, usecols=[2, 3]).T
    timestamps = np.empty(dates.shape, dtype=datetime.datetime)
    for i, day in enumerate(dates):
        timestamps[i] = datetime.datetime.strptime(day[:4] + '/' + day[4:6] + '/' + day[6:8] + '/' + times[i][:2] + '/' + times[i][2:4], '%Y/%m/%d/%H/%M')
    series_data = [timestamps, ws, wd]
    return series_data


# The idea of parse_time is that it will break the time series data into sections where the wind direction is roughly similar (within 10 degrees)
# then, each section of the time series will be fed to the simulation separately, with a differently (optimally) shifted farm.
# def parse_time(series_data):


def sim_time_series(series_data, turbine, farm_width=5, farm_length=5, width_spacing=5, length_spacing=7):
    # start by analyzing the input time_series
    [time_stamps, ws, wd] = series_data
    ten_deg_bins = np.linspace(0, 360, 37)
    wind_rose = np.histogram(wd, ten_deg_bins)
    primary_heading = wind_rose[1][wind_rose[0].argmax()]
    # create the site
    Site = SiteFromSeries(series_data, plot=True)
    # create the intial farm
    dia = turbine.diameter()
    initial_farm = WindFarm(generate_layout(farm_length, length_spacing*dia, farm_width, width_spacing*dia, heading_deg=primary_heading))

    wf_model = PropagateDownwind(MyBiSite(), turbine, wake_deficitModel=dm.NOJDeficit())
    parse_time()
    sim_res_time = wf_model(farm_ex.wt_x, farm_ex.wt_y,  # wind turbine positions
                            wd=wd,  # Wind direction time series
                            ws=ws,  # Wind speed time series
                            time=time_stamps,  # time stamps
                            TI=ti,  # turbulence intensity time series
                            operating=operating  # time dependent operating variable
                            )


def main():
    wt = NREL15()
    dia = wt.diameter()
    series_data = read_vortex("WindData/Random/758955.6m_100m_UTC_04.0_ERA5.txt")
    print(series_data)

    sim_time_series(series_data, wt)



if __name__ == '__main__':
    main()