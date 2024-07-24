from py_wake.site._site import UniformWeibullSite
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import datetime


# method to return weibull distribution parameters
def weibull(self, x, k, a):
    return (k / a) * (x / a) ** (k - 1) * np.exp(-(x / a) ** k)


def read_vortex(filepath: str, outname='') -> [list, list, int]:
    dates, times = np.loadtxt(filepath, delimiter=None, dtype=str, skiprows=4, usecols=[0, 1]).T
    ws, wd = np.loadtxt(filepath, delimiter=None, dtype=float, skiprows=4, usecols=[2, 3]).T
    timestamps = np.empty(dates.shape, dtype=datetime.datetime)
    for i, day in enumerate(dates):
        timestamps[i] = datetime.datetime.strptime(day[:4] + '/' + day[4:6] + '/' + day[6:8] + '/' + times[i][:2] + '/' + times[i][2:4], '%Y/%m/%d/%H/%M')
    # The following steps are needed to handle the edge case where vortex hands data with bot 0 and 360 degree headings.
    wd =[360 if x == 0 else x for x in wd]
    # return to regularly scheduled coding
    series_data = [timestamps, ws, wd, outname]
    return series_data


# definition of site types
class EastBlowHornsrevSite(UniformWeibullSite):
    def __init__(self, ti=.1, shear=None, plot=False):
        f = [3.597152, 3.948682, 5.167395, 7.000154, 8.364547, 6.43485,
             8.643194, 11.77051, 15.15757, 14.73792, 10.01205, 5.165975]
        a = [9.176929, 9.782334, 9.531809, 9.909545, 10.04269, 9.593921,
             9.584007, 10.51499, 11.39895, 11.68746, 11.63732, 10.08803]
        k = [2.392578, 2.447266, 2.412109, 2.591797, 2.755859, 2.595703,
             2.583984, 2.548828, 2.470703, 2.607422, 2.626953, 2.326172]
        UniformWeibullSite.__init__(self, np.array(f) / np.sum(f), a, k, ti=ti, shear=shear)
        self.dominant = np.argmax(np.array(f))*360/len(f)
        if plot:
            self.plot_wd_distribution(n_wd=12, ws_bins=[0, 5, 10, 15, 20, 25])
            plt.show()


# my attempt to make a site instance that is automatic based on time-series data
class SiteFromSeries(UniformWeibullSite):
    def __init__(self, series_data, ti=0.1, shear=None, plot=False):
        [time_stamps, ws, wd, outname] = series_data
        ten_deg_bins = np.linspace(0, 360, 37)
        wind_rose = np.histogram(wd, ten_deg_bins)
        primary_heading = wind_rose[1][wind_rose[0].argmax()]
        self.dominant = primary_heading
        f = wind_rose[0]
        a = []
        k = []
        # get all wind speeds within a wind direction bin
        for i, upper_lim in enumerate(ten_deg_bins[1:]):
            bin_speed = np.empty(0)
            for j, speed in enumerate(ws):
                if upper_lim > wd[j] >= upper_lim-10:
                    bin_speed = np.append(bin_speed, speed)
            if bin_speed.size != 0:
                weib_fit = stats.exponweib.fit(bin_speed, floc=0, f0=1)
                a.append(weib_fit[3])
                k.append(weib_fit[1])
            else:
                a.append(0)
                k.append(0)
        UniformWeibullSite.__init__(self, f / np.sum(f), a, k, ti=ti, shear=shear)
        if plot:
            print([f, a, k])
            self.plot_wd_distribution(n_wd=12, ws_bins=[0, 5, 10, 15, 20, 25])
            plt.title(f'{outname} Site Wind Rose')
            plt.show()


# a very simple extreme bifurcated site version of HornsRev
class MyBiSite(UniformWeibullSite):
    def __init__(self, ti=.1, shear=None, plot=False):
        f = [1, 0, 0, 0.7, 0, 0, 0, 0, 0, 0, 0, 0]
        a = [9.176929, 9.782334, 9.531809, 9.909545, 10.04269, 9.593921,
             9.584007, 10.51499, 11.39895, 11.68746, 11.63732, 10.08803]
        k = [2.392578, 2.447266, 2.412109, 2.591797, 2.755859, 2.595703,
             2.583984, 2.548828, 2.470703, 2.607422, 2.626953, 2.326172]
        UniformWeibullSite.__init__(self, np.array(f) / np.sum(f), a, k, ti=ti, shear=shear)
        self.dominant = np.argmax(np.array(f))*360/len(f)
        if plot:
            self.plot_wd_distribution(n_wd=12, ws_bins=[0, 5, 10, 15, 20, 25])
            plt.show()


# a very simple extreme trifurcated site version of HornsRec
class MyTriSite(UniformWeibullSite):
    def __init__(self, ti=.1, shear=None, plot=False):
        f = [1, 0, 0, 0.7, 0, 0.4, 0, 0, 0, 0, 0, 0]
        a = [9.176929, 9.782334, 9.531809, 9.909545, 10.04269, 9.593921,
             9.584007, 10.51499, 11.39895, 11.68746, 11.63732, 10.08803]
        k = [2.392578, 2.447266, 2.412109, 2.591797, 2.755859, 2.595703,
             2.583984, 2.548828, 2.470703, 2.607422, 2.626953, 2.326172]
        UniformWeibullSite.__init__(self, np.array(f) / np.sum(f), a, k, ti=ti, shear=shear)
        self.dominant = max(f)
        if plot:
            self.plot_wd_distribution(n_wd=12, ws_bins=[0, 5, 10, 15, 20, 25])
            plt.show()



