# This file written by Seamus Flannery
# my main file for testing my methods that use weibull site data and calculating possible relocation upsides
# This runs full support for static farms, and has flexible layout optimization methods
# which can be used for dynamic farm simulation in TimeSeriesSim.py
import random
from py_wake import np
from matplotlib import pyplot as plt
import math
from py_wake.wind_farm_models import PropagateDownwind
from py_wake import deficit_models as dm
from sites import EastBlowHornsrevSite, MyBiSite, MyTriSite, SiteFromSeries
from turbines import V80, NREL15
from sites import read_vortex


# data structure for turbines to hold position and facilitate position changes
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


# data structure to organize groups of turbines into farm layouts with easily accessible movement methods and
# coordinate lists to hand to PyWake
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


# method to plot the power and ct curve of turbine - used diagnostically, not in simulation
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


# deprecated method to generate a hard-coded test farm
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


# flexible method for generating rectilinear farm layouts that take a heading and a shift
# (basically can create any parallelogram)
def generate_layout(y, y_spacing, x, x_spacing, shift=0, heading_deg=0):
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


# deprecated initial test method for a dynamic farm that moved turbines at random - only losses for AEP haha
def test_random(farm, turbine, rad_range=1000, iterations=100, granularity=10, plot=False):
    radius_list = np.linspace(0, rad_range, int(rad_range / granularity + 1))
    Sim = PropagateDownwind(MyTriSite(), turbine, wake_deficitModel=dm.NOJDeficit())
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


# this takes a farm and measures its AEP for a given wind heading at a bunch of shift values, which creates
# an optimization curve. The max of that curve is returned as opt_shift and can be used to determine an optimal
# static farm or fill values in a 360 degree lookup table for a dynamic farm.
def test_perp_slide(site, farm, turbine, slide_start, slide_end, granularity=50, plot=True,
                    flow_plot=False, time_series_dir='', wd=''):
    farm_heading = farm.heading
    wind_direction = site.dominant
    if wd != '':
        wind_direction = wd
    if time_series_dir != '':
        wind_direction = time_series_dir
    slide_range = slide_end - slide_start
    radius_list = np.linspace(slide_start, slide_end, int(slide_range / granularity + 1))
    Sim = PropagateDownwind(site, turbine, wake_deficitModel=dm.NOJDeficit())
    # run the simulation for Annual Energy Production (AEP)
    simulationResult = Sim(farm.wt_x, farm.wt_y)
    AEP = float(simulationResult.aep(normalize_probabilities=True).sum())
    results = np.zeros(int(slide_range / granularity + 1))
    for i, rad in enumerate(radius_list):
        farm.perp_slide(rad, wind_direction)
        simulation = Sim(farm.wt_x, farm.wt_y)
        mapsim = Sim(farm.wt_x, farm.wt_y)
        results[i] = float(simulation.aep(normalize_probabilities=True).sum())
        if flow_plot and i % 10 == 0:
            wind_speed = 10
            wind_direction = 30   # TODO why is this value affecting AEP?!?!?!?!
            flow_map = mapsim.flow_map(ws=wind_speed, wd=wind_direction)
            plt.figure()
            flow_map.plot_wake_map()
            plt.xlabel('x [m]')
            plt.ylabel('y [m]')
            plt.grid()
            plt.title('Wake map for' + f' {wind_speed} m/s, {wind_direction} deg, {rad} m stationholding radius')
            plt.show()
    max_aep = results.max()  # this could be upgraded using an interpolation or a derivative sensitive granularity
    opt_shift = radius_list[results.argmax()]
    steps = len(results)
    if plot:
        plt.plot(radius_list, results)
        print("max aep: " + str(max_aep) + " GWh")
        print("max aep at shift: " + str(opt_shift) + " m")
        plt.xlabel("slide (m)")
        plt.ylabel("AEP (GWh)")
        plt.title("Annual Energy Production Vs. Wind-perpendicular Slide Tolerance")
        plt.show()
    return max_aep, opt_shift, steps


# NOW DEPRECATED attempt to get higher res data around extrema with less computation - runge-kutta 4th order?
def efficient_perp_slide(site, farm, turbine, wind_direction=0, slide_range=100, plot=True, flow_plot=False):
    farm_heading = farm.heading
    radius = 0
    Sim = PropagateDownwind(site, turbine, wake_deficitModel=dm.NOJDeficit())
    # run the simulation for Annual Energy Production (AEP)
    init_result = Sim(farm.wt_x, farm.wt_y)
    AEP = float(init_result.aep(normalize_probabilities=True).sum())
    results = np.array(AEP)
    radius_list = np.array(radius)
    slide_factor = 1
    radius += slide_factor
    while radius <= slide_range:
        farm.perp_slide(radius, wind_direction)
        next_result = Sim(farm.wt_x, farm.wt_y)
        AEP = float(next_result.aep(normalize_probabilities=True).sum())
        results = np.append(results, AEP)
        radius_list = np.append(radius_list, radius)
        dAEP = abs(results[-1] - results[-2])
        if dAEP <= 4:
            slide_factor *= 1.2
        else:
            slide_factor *= 0.8
        radius += slide_factor
        print(radius)
    max_aep = results.max()  # this could be upgraded using an interpolation or a derivative sensitive granularity
    opt_shift = radius_list[results.argmax()]
    steps = len(results)
    if plot:
        plt.plot(radius_list, results)
        print("max aep: " + str(max_aep) + " GWh")
        print("max aep at shift: " + str(opt_shift) + " m")
        plt.xlabel("slide (m)")
        plt.ylabel("AEP (GWh)")
        plt.title("Annual Energy Production Vs. Wind-perpendicular Slide Tolerance")
        plt.show()
    return max_aep, opt_shift, steps


# generates a farm with 0 shift, output will give shift value to optimize that layout for a given wind condition
# takes spacing in multiples of turbine Diameter. Overlaps significantly in function with test_perp_slide but is a
# little simpler to use. This also returns the shifted farm for future use.
def find_opt_shift(site, turbine, farm_width, farm_length, width_spacing, length_spacing, heading_deg=0, plot=False):
    dia = turbine.diameter()
    hub = turbine.hub_height()
    farm = WindFarm(generate_layout(farm_width, dia * width_spacing, farm_length, dia * length_spacing, 0, heading_deg=heading_deg))
    max_aep, opt_shift, steps = test_perp_slide(site, farm, turbine, - dia * width_spacing, dia * width_spacing,
                                                granularity=dia * 0.1, plot=plot)
    opt_farm = WindFarm(generate_layout(farm_width, dia * width_spacing, farm_length, dia * length_spacing, opt_shift, heading_deg=heading_deg))
    # opt_sim = PropagateDownwind(site, turbine, wake_deficitModel=dm.NOJDeficit())
    # simulationResult = opt_sim(opt_farm.wt_x, opt_farm.wt_y)
    # AEP = float(simulationResult.aep(normalize_probabilities=True).sum())
    print("Max AEP: " + str(max_aep))
    print("Opt Shift: " + str(opt_shift) + ", w/ width spacing: " + str(width_spacing * dia) + ", representing a " + str(opt_shift/dia) + "D shift, a " + str(opt_shift/width_spacing/dia) + " multiple of the turbine spacing.")
    return max_aep, opt_shift, opt_farm


# NOT USED - some ideas from this got incorporated into the dynamic farm simulation but this was before
# I decided it needed to be a time-series function (I had initially thought that PyWake would adequately tell me
# about dynamic farms with statistical data rather than a direct time series; this was incorrect)
# the goal of this function would be to optimize a farm based on a simple site, then run it against a more complex
# site to see if there's an AEP upside to the perpendicular slide from the already optimized shift
# if I figure out the right metrics, I could possibly try to then subtract the simple site from the complex site
# and compare that wind difference against the AEP upside.
def trifurcate_upside(simple_site, complex_site, turbine, farm_width, farm_length, width_spacing=5, length_spacing=7):
    dia = turbine.diameter()
    w_spacing_m, l_spacing_m = dia*width_spacing, dia*length_spacing
    init_AEP, init_shift, opt_farm = find_opt_shift(simple_site, turbine, farm_width, farm_length, width_spacing, length_spacing, plot=False)
    opt_sim = PropagateDownwind(complex_site, turbine, wake_deficitModel=dm.NOJDeficit())
    immobileResult = opt_sim(opt_farm.wt_x, opt_farm.wt_y)
    opt_AEP = float(immobileResult.aep(normalize_probabilities=True).sum())
    max_complex_AEP, approx_shift, steps = test_perp_slide(complex_site, opt_farm, turbine, -w_spacing_m, w_spacing_m)
    upside = max_complex_AEP - opt_AEP
    upside_percent = (max_complex_AEP - opt_AEP)/opt_AEP * 100
    print("The potential upside is " + str(upside) + " GWh, (~" + str(int(upside_percent)) + "%) and the approximate shift distance is " + str(approx_shift) + "m.")
    return upside, approx_shift


# working/testing main function
def main():
    # test_perp_slide(TenFarm, wt, slide_range=200, granularity=10)
    wt = NREL15()
    five_d = wt.diameter() * 5
    seven_d = wt.diameter() * 7
    # print('Diameter', wt.diameter())
    # print('Hub height', wt.hub_height())
    # TenXNRELFarm = WindFarm(generate_layout(10, wt.diameter()*5, 10, wt.diameter()*7, 590))
    # test_perp_slide(MyBiSite(), TenXNRELFarm, wt, granularity=wt.diameter()*0.1, plot=True)
    # print(test_perp_slide(MySite(), WindFarm(generate_layout(5, five_d, 5, seven_d, 0)), wt, slide_range=2000))
    # print(efficient_perp_slide(MySite(), WindFarm(generate_layout(5, five_d, 5, seven_d, 0)), wt, slide_range=2000))
    # find_opt_shift(MyBiSite(), wt, 5, 5, 5, 7, plot=False)
    print(trifurcate_upside(MyBiSite(), MyTriSite(), V80(), 5, 5))
    series_data = read_vortex("WindData/Chile/758955.6m_100m_UTC_04.0_ERA5.txt", outname="Spain Site")
    horns_rev_series = read_vortex("WindData/HornsRev/761517.6m_100m_UTC+02.0_ERA5.txt", outname='HornsRev')
    spain_series_site = SiteFromSeries(series_data)
    Horns_rev_series_site = SiteFromSeries(horns_rev_series)
    print(f'Upside from Spain series: {trifurcate_upside()}')
    print(f'')
    # test_perp_slide(RotTenFarm, wt, slide_range=100, granularity=10, plot=True)
    # plot_p_ct()

# ignore this (clearly trifurcated sites were never found on vortex, and this would need to be a dynamic sim anyway)
# TODO write a new function that automatically optimizes the initial farm slide according to bifurcated wind,
# TODO and then tests in trifurcated wind


if __name__ == '__main__':
    main()
