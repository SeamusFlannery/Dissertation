# this is a copy site of the hornsrev site file. I may edit this to test things
import copy
import random
from py_wake import np
from matplotlib import pyplot as plt
import math
from py_wake.wind_farm_models import PropagateDownwind
from py_wake import deficit_models as dm
from py_wake.site._site import UniformWeibullSite
from py_wake.wind_turbines import WindTurbine
from py_wake.wind_turbines.power_ct_functions import PowerCtTabular
from p_ct_curves import V80ct_curve, V80power_curve, NREL15power_curve, NREL15ct_curve


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


# [1] E. Gaertner et al., “Definition of the IEA Wind 15-Megawatt Offshore Reference Wind Turbine,” NREL/TP-5000-75698, Mar. 2020. [Online]. Available: https://www.nrel.gov/docs/fy20osti/75698.pdf
class NREL15(WindTurbine):
    def __init__(self, method='linear'):
        WindTurbine.__init__(self, name='NREL15', diameter=240, hub_height=150,
                             powerCtFunction=PowerCtTabular(NREL15power_curve[:, 0], NREL15power_curve[:, 1], 'w',
                                                            NREL15ct_curve[:, 1], method=method))


class Turbine_instance:
    def __init__(self, x, y):
        self.origin_x = x
        self.origin_y = y
        self.pos = [self.origin_x, self.origin_y]

    def move(self, x_add, y_add):
        self.pos = [self.origin_x + x_add, self.origin_y + y_add]

    def random_move(self, radius):
        # generate random, even distributed point in polar coordinates
        theta = 2 * math.pi * random.random()
        r = radius * math.sqrt(random.random())
        # convert to cartesian
        x = r * math.cos(theta) + self.origin_x
        y = r * math.sin(theta) + self.origin_y
        self.pos = [x, y]


class WindFarm:
    def __init__(self, turbine_list, heading=0):
        self.turbines = turbine_list
        self.wt_x, self.wt_y = [], []
        self.heading = heading
        for i, turbine in enumerate(turbine_list):
            self.wt_x.append(turbine.pos[0])
            self.wt_y.append(turbine.pos[1])

    def random_move(self, radius):
        for i, turbine in enumerate(self.turbines):
            turbine.random_move(radius)
            self.wt_x[i], self.wt_y[i] = turbine.pos

    def perp_slide(self, distance, wind_direction):
        rows = int(math.sqrt(len(self.turbines)))
        row_count = -1
        add_x = distance * math.cos(math.radians(wind_direction))
        add_y = distance * math.sin(math.radians(wind_direction))
        for i, turbine in enumerate(self.turbines):
            if i % rows == 0:
                row_count += 1
            turbine.move(add_x * row_count, add_y * row_count)
            self.wt_x[i], self.wt_y[i] = turbine.pos


def plot_p_ct():
    wt = V80()
    ws = np.linspace(3, 20, 100)
    plt.plot(ws, wt.power(ws) * 1e-3, label='Power')
    c = plt.plot([], [], label='Ct')[0].get_color()
    plt.ylabel('Power [kW]')
    ax = plt.gca().twinx()
    ax.plot(ws, wt.ct(ws), color=c)
    ax.set_ylabel('Ct')
    plt.xlabel('Wind speed [m/s]')
    plt.gcf().axes[0].legend(loc=1)
    plt.show()


def simple_farm_maker():
    t_1 = Turbine_instance(0, 1000)
    t_2 = Turbine_instance(500, 1000)
    t_3 = Turbine_instance(1000, 1000)
    t_4 = Turbine_instance(0, 500)
    t_5 = Turbine_instance(500, 500)
    t_6 = Turbine_instance(1000, 500)
    t_7 = Turbine_instance(0, 0)
    t_8 = Turbine_instance(500, 0)
    t_9 = Turbine_instance(1000, 0)
    turbine_list = [t_1, t_2, t_3, t_4, t_5, t_6, t_7, t_8, t_9]
    simple_farm = WindFarm(turbine_list)
    return simple_farm


class EastBlowHornsrevSite(UniformWeibullSite):
    def __init__(self, ti=.1, shear=None):
        f = [3.597152, 3.948682, 5.167395, 7.000154, 8.364547, 6.43485,
             8.643194, 11.77051, 15.15757, 14.73792, 10.01205, 5.165975]
        a = [9.176929, 9.782334, 9.531809, 9.909545, 10.04269, 9.593921,
             9.584007, 10.51499, 11.39895, 11.68746, 11.63732, 10.08803]
        k = [2.392578, 2.447266, 2.412109, 2.591797, 2.755859, 2.595703,
             2.583984, 2.548828, 2.470703, 2.607422, 2.626953, 2.326172]
        UniformWeibullSite.__init__(self, np.array(f) / np.sum(f), a, k, ti=ti, shear=shear)
        # to plot windrose, un-comment below
        # self.plot_wd_distribution(n_wd=12, ws_bins=[0, 5, 10, 15, 20, 25])


class MySite(UniformWeibullSite):
    def __init__(self, ti=.1, shear=None):
        f = [1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0]
        a = [9.176929, 9.782334, 9.531809, 9.909545, 10.04269, 9.593921,
             9.584007, 10.51499, 11.39895, 11.68746, 11.63732, 10.08803]
        k = [2.392578, 2.447266, 2.412109, 2.591797, 2.755859, 2.595703,
             2.583984, 2.548828, 2.470703, 2.607422, 2.626953, 2.326172]
        UniformWeibullSite.__init__(self, np.array(f) / np.sum(f), a, k, ti=ti, shear=shear)
        # to plot windrose, un-comment below
        # self.plot_wd_distribution(n_wd=12, ws_bins=[0, 5, 10, 15, 20, 25])
        # plt.show()


def generate_layout(y, y_spacing, x, x_spacing, shift, heading_deg=0):
    layout = np.empty([y, x], list)
    for i in range(y):
        for j in range(x):
            x_pos = j * x_spacing + i * shift
            y_pos = y * y_spacing - (i + 1) * y_spacing
            layout[i, j] = [x_pos, y_pos]
    if heading_deg != 0:
        heading = math.radians(heading_deg)
        [center_x, center_y] = [x / 2 * x_spacing + shift * x / 2, y / 2 * y_spacing]
        for i in range(y):
            for j in range(x):
                [old_x, old_y] = layout[i, j]
                vector = [center_x - old_x, center_y - old_y]
                rotated_vector = [math.cos(heading) * vector[0] - math.sin(heading) * vector[1],
                                  math.sin(heading) * vector[0] + math.cos(heading) * vector[1]]
                [new_x, new_y] = [center_x + rotated_vector[0], center_y + rotated_vector[1]]
                layout[i, j] = [new_x, new_y]
    turbine_list = []
    for column in layout:
        for location in column:
            turbine_list.append(Turbine_instance(location[0], location[1]))
    return turbine_list


def test_random(farm, turbine, rad_range=1000, iterations=100, granularity=10, plot=False):
    radius_list = np.linspace(0, rad_range, int(rad_range / granularity + 1))
    Sim = PropagateDownwind(MySite(), turbine, wake_deficitModel=dm.NOJDeficit())
    # run the simulation for Annual Energy Production (AEP)
    simulationResult = Sim(farm.wt_x, farm.wt_y)
    AEP = float(simulationResult.aep(normalize_probabilities=False).sum())
    results = np.zeros(int(rad_range / granularity + 1))
    conf_ints = np.zeros(int(rad_range / granularity + 1))
    for i, rad in enumerate(radius_list):
        prod_list = []
        for j in range(iterations):
            farm.random_move(rad)
            simulation = Sim(farm.wt_x, farm.wt_y)
            prod_list.append(float(simulation.aep(normalize_probabilities=False).sum()))
        avg = np.average(prod_list)
        stdv = np.std(prod_list)
        conf_int = 1.96 * stdv / np.sqrt(len(prod_list))
        results[i] = avg
        conf_ints[i] = conf_int
        if plot and i % 10 == 0:
            plt.figure()
            wind_speed = 10
            wind_direction = 0
            flow_map = simulation.flow_map(ws=wind_speed, wd=wind_direction)
            plt.figure()
            flow_map.plot_wake_map()
            plt.xlabel('x [m]')
            plt.ylabel('y [m]')
            plt.grid()
            plt.title('Wake map for' + f' {wind_speed} m/s, {wind_direction} deg, {rad} m stationholding radius')
            plt.show()
    plt.plot(radius_list, results)
    plt.plot(radius_list, np.add(results, conf_ints))
    plt.plot(radius_list, np.add(results, -1 * conf_ints))
    # plt.plot(radius_list, AEP)
    plt.show()


def test_perp_slide(farm, turbine, wind_direction=0, slide_range=100, granularity=10, plot=False):
    farm_heading = farm.heading
    radius_list = np.linspace(0, slide_range, int(slide_range / granularity + 1))
    Sim = PropagateDownwind(MySite(), turbine, wake_deficitModel=dm.NOJDeficit())
    # run the simulation for Annual Energy Production (AEP)
    simulationResult = Sim(farm.wt_x, farm.wt_y)
    AEP = float(simulationResult.aep(normalize_probabilities=True).sum())
    results = np.zeros(int(slide_range / granularity + 1))
    for i, rad in enumerate(radius_list):
        farm.perp_slide(rad, wind_direction)
        simulation = Sim(farm.wt_x, farm.wt_y)
        mapsim = Sim(farm.wt_x, farm.wt_y)
        results[i] = float(simulation.aep(normalize_probabilities=True).sum())
        if plot and i % 10 == 0:
            wind_speed = 10
            wind_direction = 30  ## TODO why is this value affecting AEP?!?!?!?!
            flow_map = mapsim.flow_map(ws=wind_speed, wd=wind_direction)
            plt.figure()
            flow_map.plot_wake_map()
            plt.xlabel('x [m]')
            plt.ylabel('y [m]')
            plt.grid()
            plt.title('Wake map for' + f' {wind_speed} m/s, {wind_direction} deg, {rad} m stationholding radius')
            plt.show()
    plt.plot(radius_list, results)
    print("max aep: " + str(results.max()) + " GWh")
    print("max aep at shift: " + str(radius_list[results.argmax()]) + " m")
    plt.xlabel("slide (m)")
    plt.ylabel("AEP (GWh)")
    plt.title("Annual Energy Production Vs. Wind-perpendicular Slide Tolerance")
    plt.show()


def main():
    # wt = V80()
    # print('Diameter', wt.diameter())
    # print('Hub height', wt.hub_height())
    # test_random(simple_farm, wt, rad_range=50, iterations=1000, granularity=1, plot=True)
    # test_perp_slide(simple_farm, wt, slide_range=500, granularity=10)
    # print(generate_layout(3, 500, 3, 500, 0))
    # TenFarm = WindFarm(generate_layout(10, 500, 10, 500, 150))
    # RotTenFarm = WindFarm(generate_layout(10, 500, 10, 500, 0, heading_deg=45), heading=45)
    # test_perp_slide(TenFarm, wt, slide_range=200, granularity=10)
    wt = NREL15()
    print('Diameter', wt.diameter())
    print('Hub height', wt.hub_height())
    TenXNRELFarm = WindFarm(generate_layout(10, wt.diameter()*5, 10, wt.diameter()*7, 590))
    test_perp_slide(TenXNRELFarm, wt, slide_range=wt.diameter()*4, granularity=wt.diameter()*0.1)
    # test_perp_slide(RotTenFarm, wt, slide_range=100, granularity=10, plot=True)
    # plot_p_ct()

# TODO write a new function that automatically optimizes the initial farm slide according to bifurcated wind,
# TODO and then tests in trifurcated wind

if __name__ == '__main__':
    main()
