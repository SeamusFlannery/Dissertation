# Written/Compiled by Seamus Flannery, this file holds turbine class objects for use in PyWake
from py_wake.wind_turbines import WindTurbine
from py_wake.wind_turbines.power_ct_functions import PowerCtTabular
from p_ct_curves import V80ct_curve, V80power_curve, NREL15power_curve, NREL15ct_curve


# This class holds the information for the NREL 15 MW standard turbine and uses a power curve found at
# the citation below, taken from the device definition publication and associated GitHub.
# [1] E. Gaertner et al., “Definition of the IEA Wind 15-Megawatt Offshore Reference Wind Turbine,” NREL/TP-5000-75698, Mar. 2020. [Online]. Available: https://www.nrel.gov/docs/fy20osti/75698.pdf
class NREL15(WindTurbine):
    def __init__(self, method='linear'):
        WindTurbine.__init__(self, name='NREL15', diameter=240, hub_height=150,
                             powerCtFunction=PowerCtTabular(NREL15power_curve[:, 0], NREL15power_curve[:, 1], 'w',
                                                            NREL15ct_curve[:, 1], method=method))


# This class from the PyWake documentation holds the information for the Vestas 80m turbine.
class V80(WindTurbine):
    def __init__(self, method='linear'):
        """
        Parameters
        ----------
        method : {'linear', 'pchip'}
            linear(fast) or pchip(smooth and gradient friendly) interpolation
        """
        WindTurbine.__init__(self, name='V80', diameter=80, hub_height=70,
                             powerCtFunction=PowerCtTabular(V80power_curve[:, 0], V80power_curve[:, 1], 'w',
                                                            V80ct_curve[:, 1], method=method))
