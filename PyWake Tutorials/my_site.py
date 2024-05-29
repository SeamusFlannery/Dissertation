# this is a copy site of the hornsrev site file. I may edit this to test things
import random
from py_wake import np
from matplotlib import pyplot as plt
import math
from py_wake.wind_farm_models import PropagateDownwind
from py_wake import deficit_models as dm
from py_wake.site._site import UniformWeibullSite
from py_wake.wind_turbines import WindTurbine
from py_wake.wind_turbines.power_ct_functions import PowerCtTabular


class V80(WindTurbine):
    def __init__(self, method='linear'):
        """
        Parameters
        ----------
        method : {'linear', 'pchip'}
            linear(fast) or pchip(smooth and gradient friendly) interpolation
        """
        WindTurbine.__init__(self, name='V80', diameter=80, hub_height=70,
                             powerCtFunction=PowerCtTabular(power_curve[:, 0], power_curve[:, 1], 'w',
                                                            ct_curve[:, 1], method=method))


class Turbine_instance:
    def __init__(self, x, y):
        self.origin_x = x
        self.origin_y = y
        self.pos = [self.origin_x, self.origin_y]

    def move(self, x_add, y_add):
        self.pos = [self.origin_x+x_add, self.origin_y + y_add]

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
            turbine.move(add_x*row_count, add_y*row_count)
            self.wt_x[i], self.wt_y[i] = turbine.pos


power_curve = np.array(
    [[3.0, 0.0], [4.0, 66.6], [5.0, 154.0], [6.0, 282.0], [7.0, 460.0], [8.0, 696.0], [9.0, 996.0], [10.0, 1341.0],
     [11.0, 1661.0], [12.0, 1866.0], [13.0, 1958.0], [14.0, 1988.0], [15.0, 1997.0], [16.0, 1999.0], [17.0, 2000.0],
     [18.0, 2000.0], [19.0, 2000.0], [20.0, 2000.0], [21.0, 2000.0], [22.0, 2000.0], [23.0, 2000.0], [24.0, 2000.0],
     [25.0, 2000.0]]) * [1, 1000]
ct_curve = np.array([[3.0, 0.0],
                     [4.0, 0.818],
                     [5.0, 0.806],
                     [6.0, 0.804],
                     [7.0, 0.805],
                     [8.0, 0.806],
                     [9.0, 0.807],
                     [10.0, 0.793],
                     [11.0, 0.739],
                     [12.0, 0.709],
                     [13.0, 0.409],
                     [14.0, 0.314],
                     [15.0, 0.249],
                     [16.0, 0.202],
                     [17.0, 0.167],
                     [18.0, 0.14],
                     [19.0, 0.119],
                     [20.0, 0.102],
                     [21.0, 0.088],
                     [22.0, 0.077],
                     [23.0, 0.067],
                     [24.0, 0.06],
                     [25.0, 0.053]])
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
wt_x, wt_y = simple_farm.wt_x, simple_farm.wt_y
print(simple_farm.wt_x, simple_farm.wt_y)


class MySite(UniformWeibullSite):
    def __init__(self, ti=.1, shear=None):
        f = [3.597152, 3.948682, 5.167395, 7.000154, 8.364547, 6.43485,
             8.643194, 11.77051, 15.15757, 14.73792, 10.01205, 5.165975]
        a = [9.176929, 9.782334, 9.531809, 9.909545, 10.04269, 9.593921,
             9.584007, 10.51499, 11.39895, 11.68746, 11.63732, 10.08803]
        k = [2.392578, 2.447266, 2.412109, 2.591797, 2.755859, 2.595703,
             2.583984, 2.548828, 2.470703, 2.607422, 2.626953, 2.326172]
        UniformWeibullSite.__init__(self, np.array(f) / np.sum(f), a, k, ti=ti, shear=shear)
        self.initial_position = np.array([wt_x, wt_y]).T


def generate_layout(y, y_spacing, x, x_spacing, shift, heading_deg=0):
    layout = np.empty([y, x], list)
    for i in range(y):
        for j in range(x):
            x_pos = j*x_spacing + i*shift
            y_pos = y*y_spacing - (i+1)*y_spacing
            layout[i, j] = [x_pos, y_pos]
    if heading_deg != 0:
        heading = math.radians(heading_deg)
        [center_x, center_y] = [x/2*x_spacing + shift*x/2, y/2*y_spacing]
        for i in range(y):
            for j in range(x):
                [old_x, old_y] = layout[i, j]
                vector = [center_x-old_x, center_y-old_y]
                rotated_vector = [math.cos(heading)*vector[0] - math.sin(heading)*vector[1], math.sin(heading)*vector[0]+math.cos(heading)*vector[1]]
                [new_x, new_y] = [center_x+rotated_vector[0], center_y+rotated_vector[1]]
                layout[i, j] = [new_x, new_y]
    turbine_list = []
    for column in layout:
        for location in column:
            turbine_list.append(Turbine_instance(location[0], location[1]))
    return turbine_list


def test_random(farm, turbine, rad_range=1000, iterations=100, granularity=10, plot=False):
    radius_list = np.linspace(0, rad_range, int(rad_range/granularity+1))
    Sim = PropagateDownwind(MySite(), turbine, wake_deficitModel=dm.NOJDeficit())
    # run the simulation for Annual Energy Production (AEP)
    simulationResult = Sim(farm.wt_x, farm.wt_y)
    AEP = float(simulationResult.aep(normalize_probabilities=True).sum())
    results = np.zeros(int(rad_range/granularity+1))
    conf_ints = np.zeros(int(rad_range/granularity+1))
    for i, rad in enumerate(radius_list):
        prod_list = []
        for j in range(iterations):
            farm.random_move(rad)
            simulation = Sim(farm.wt_x, farm.wt_y)
            prod_list.append(float(simulation.aep(normalize_probabilities=True).sum()))
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
    plt.plot(radius_list, np.add(results, -1*conf_ints))
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
        results[i] = float(simulation.aep(normalize_probabilities=True).sum())
        if plot and i % 10 == 0:
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
    plt.xlabel("slide (m)")
    plt.ylabel("AEP (GWh)")
    plt.title("Annual Energy Production Vs. Wind-perpendicular Slide Tolerance")
    plt.show()


def main():
    wt = V80()
    print('Diameter', wt.diameter())
    print('Hub height', wt.hub_height())
    # test_random(simple_farm, wt, rad_range=50, iterations=1000, granularity=1, plot=True)
    # test_perp_slide(simple_farm, wt, slide_range=500, granularity=10)
    # print(generate_layout(3, 500, 3, 500, 0))
    TenFarm = WindFarm(generate_layout(10, 500, 10, 500, 100))
    RotTenFarm = WindFarm(generate_layout(10, 500, 10, 500, 0, heading_deg=45), heading=45)
    test_perp_slide(TenFarm, wt, slide_range=100, granularity=10, plot=True)
    test_perp_slide(RotTenFarm, wt, slide_range=100, granularity=10, plot=True)
    # plot_p_ct()


main()
