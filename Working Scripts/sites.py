from py_wake.site._site import UniformWeibullSite
import numpy as np
import matplotlib.pyplot as plt


class EastBlowHornsrevSite(UniformWeibullSite):
    def __init__(self, ti=.1, shear=None, plot=False):
        f = [3.597152, 3.948682, 5.167395, 7.000154, 8.364547, 6.43485,
             8.643194, 11.77051, 15.15757, 14.73792, 10.01205, 5.165975]
        a = [9.176929, 9.782334, 9.531809, 9.909545, 10.04269, 9.593921,
             9.584007, 10.51499, 11.39895, 11.68746, 11.63732, 10.08803]
        k = [2.392578, 2.447266, 2.412109, 2.591797, 2.755859, 2.595703,
             2.583984, 2.548828, 2.470703, 2.607422, 2.626953, 2.326172]
        UniformWeibullSite.__init__(self, np.array(f) / np.sum(f), a, k, ti=ti, shear=shear)
        self.dominant = max(f)
        if plot:
            self.plot_wd_distribution(n_wd=12, ws_bins=[0, 5, 10, 15, 20, 25])
            plt.show()


class MyBiSite(UniformWeibullSite):
    def __init__(self, ti=.1, shear=None, plot=False):
        f = [1, 0, 0, 0.7, 0, 0, 0, 0, 0, 0, 0, 0]
        a = [9.176929, 9.782334, 9.531809, 9.909545, 10.04269, 9.593921,
             9.584007, 10.51499, 11.39895, 11.68746, 11.63732, 10.08803]
        k = [2.392578, 2.447266, 2.412109, 2.591797, 2.755859, 2.595703,
             2.583984, 2.548828, 2.470703, 2.607422, 2.626953, 2.326172]
        UniformWeibullSite.__init__(self, np.array(f) / np.sum(f), a, k, ti=ti, shear=shear)
        self.dominant = max(f)
        if plot:
            self.plot_wd_distribution(n_wd=12, ws_bins=[0, 5, 10, 15, 20, 25])
            plt.show()


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
