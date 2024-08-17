# a tutorial file from the pyWake documentation.
import numpy as np
import matplotlib.pyplot as plt
from py_wake.examples.data.hornsrev1 import Hornsrev1Site
from py_wake.examples.data.iea37 import IEA37Site
from py_wake.examples.data.ParqueFicticio import ParqueFicticioSite
from py_wake.site import UniformWeibullSite
from py_wake.site import WaspGridSite
from py_wake.examples.data.ParqueFicticio import ParqueFicticio_path
from py_wake.examples.data.hornsrev1 import Hornsrev1Site, V80, wt_x, wt_y, wt16_x, wt16_y
from py_wake import NOJ

# init sites
sites = {"IEA37": IEA37Site(n_wt=16),
         "Hornsrev1": Hornsrev1Site(),
         "ParqueFicticio": ParqueFicticioSite()}

# specifying the necessary parameters for an example UniformWeibullSite object
site = UniformWeibullSite(p_wd=[.20, .25, .35, .25],  # sector frequencies
                          a=[9.176929, 9.782334, 9.531809, 9.909545],  # Weibull scale parameter
                          k=[2.392578, 2.447266, 2.412109, 2.591797],  # Weibull shape parameter
                          ti=0.1  # turbulence intensity, optional
                          )

# specifying an example WaSP Grid site
site = WaspGridSite.from_wasp_grd(ParqueFicticio_path)

# then use these example data sites to model


