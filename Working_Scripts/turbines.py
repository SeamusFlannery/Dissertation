from py_wake.wind_turbines import WindTurbine
from py_wake.wind_turbines.power_ct_functions import PowerCtTabular
from p_ct_curves import V80ct_curve, V80power_curve, NREL15power_curve, NREL15ct_curve


# [1] E. Gaertner et al., “Definition of the IEA Wind 15-Megawatt Offshore Reference Wind Turbine,” NREL/TP-5000-75698, Mar. 2020. [Online]. Available: https://www.nrel.gov/docs/fy20osti/75698.pdf
class NREL15(WindTurbine):
    def __init__(self, method='linear'):
        WindTurbine.__init__(self, name='NREL15', diameter=240, hub_height=150,
                             powerCtFunction=PowerCtTabular(NREL15power_curve[:, 0], NREL15power_curve[:, 1], 'w',
                                                            NREL15ct_curve[:, 1], method=method))


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
