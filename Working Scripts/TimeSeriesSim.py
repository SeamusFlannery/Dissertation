import numpy as np
import matplotlib.pyplot as plt
from Stationholding import generate_layout, WindFarm, Turbine_instance, find_opt_shift, test_perp_slide
from turbines import NREL15
from sites import MyBiSite, MyTriSite, EastBlowHornsrevSite, SiteFromSeries, read_vortex
from py_wake.wind_farm_models import PropagateDownwind
from py_wake import deficit_models as dm
import imageio
import warnings
# suppress overflow warnings that come from pywakes built-in weibull stuff
warnings.filterwarnings('ignore')


# The idea of time_chunk is that it will break the time series data into sections where the wind direction is roughly similar (within 10 degrees)
# then, each section of the time series will be fed to the simulation separately, with a differently (optimally) shifted farm.
# max_freq is given as the number of hours that must occur between repositionings. every hour = 1, every day = 24
# every six months = 365/2*24 = 4380
# hourly repositioning are easy to predict based on short-term weather, and seasonal are as well
# daily to weekly repositioning times would be problematic from a weather prediction standpoint (I'm guessing)
# this algorithm will run from the start of the time series to the end, rather than an optimized algorithm,
# as this more readily reflects reacting to weather as it comes, rather than already knowing the exact weather in the future
def time_chunk(series_data, max_freq, dir_sensitivity=20, mode='freq'):
    [times, ws, wd, outname] = series_data
    reposit_timer = 0
    chunks = []
    chunk_lengths = []
    current_chunk = []
    dom_wind_dir = wd[0]
    if mode == 'freq':
        for i, timestamp in enumerate(times):
            if reposit_timer <= max_freq:
                reposit_timer += 1
                current_chunk.append(timestamp)
            elif abs(dom_wind_dir - wd[i]) <= dir_sensitivity:  # default if wind direction is within 30, no repositioning necessary?
                current_chunk.append(timestamp)
            elif abs(dom_wind_dir - wd[i]) > dir_sensitivity:
                chunks.append(current_chunk)
                chunk_lengths.append(len(current_chunk))
                dom_wind_dir = wd[i]
                reposit_timer = 0
                current_chunk = []
        return chunks, chunk_lengths
    elif mode == "no freq":  # mode that simply groups time chunks by wind directions and then reports frequency
        for i, timestamp in enumerate(times):
            if abs(dom_wind_dir - wd[i]) <= dir_sensitivity:  # default if wind direction is within 30, no repositioning necessary?
                current_chunk.append(timestamp)
            elif abs(dom_wind_dir - wd[i]) > dir_sensitivity:
                chunks.append(current_chunk)
                chunk_lengths.append(len(current_chunk))
                dom_wind_dir = wd[i]
                current_chunk = [timestamp]
        return chunks, chunk_lengths


def sim_time_series(series_data, turbine, farm_width=5, farm_length=5, width_spacing=5, length_spacing=7, plot=False, fast=''):
    # start by analyzing the input time_series
    [time_stamps, ws, wd, outname] = series_data
    print(f'Beginning analysis of {outname}')
    ten_deg_bins = np.linspace(0, 360, 37)
    wind_rose = np.histogram(wd, ten_deg_bins)
    primary_heading = wind_rose[1][wind_rose[0].argmax()]
    # create the site
    Site = SiteFromSeries(series_data, plot=True)  # , plot=True)
    # create the intial farm
    dia = turbine.diameter()
    target_aep, shift, initial_farm = find_opt_shift(Site, turbine, farm_width, farm_length, width_spacing, length_spacing, heading_deg=primary_heading, plot=plot)
    # initial_farm = WindFarm(generate_layout(farm_length, length_spacing*dia, farm_width, width_spacing*dia, heading_deg=primary_heading))
    wf_model = PropagateDownwind(Site, turbine, wake_deficitModel=dm.NOJDeficit())
    # simulate time-series with immobile farm
    immobile_time_sim_results = wf_model(initial_farm.wt_x, initial_farm.wt_y, wd=wd, ws=ws, time=time_stamps, TI=0.1)
    immobile_AEP = float(immobile_time_sim_results.aep().sum())
    # TODO figure out what method I can use that will actually calculate the AEP for a farm accoridng only to the time series given (as below)
    # immobile_time_sim_results_test2 = wf_model(initial_farm.wt_x, initial_farm.wt_y, wd=wd[0:100], ws=ws[0:100], time=time_stamps[0:100], TI=0.1)
    # immobile_AEP_test2 = float(immobile_time_sim_results.aep().sum())
    # simulate time-series with breathing farm
    chunks, chunk_lengths = time_chunk(series_data, 20, mode='no freq')
    print(f'{len(chunks)} chunks defined')
    shift_distances = []
    shift_directions = []
    chunk_aeps = []  # TODO are these normalizeD?
    for i, chunk in enumerate(chunks):  # this could be time/computation expensive, consider switching to indexed instead of time-stamp search
        start_index = np.where(time_stamps == chunk[0])[0][0]
        end_index = start_index + chunk_lengths[i]
        chunk_times = time_stamps[start_index:end_index]
        chunk_wd = wd[start_index:end_index]
        chunk_ws = ws[start_index:end_index]
        if fast == '':
            print(f'testing for optimal responsive farm shift on chunk {i} of {len(chunks)}')
            shift = test_perp_slide(Site, initial_farm, turbine, - dia * width_spacing*0.3, dia * width_spacing*0.3,
                                granularity=dia * 0.1, plot=plot, time_series_dir=chunk_wd[0])[1]
            initial_farm.perp_slide(shift, chunk_wd[0])
            shift_distances.append(shift)
            shift_directions.append(chunk_wd[0])
            mobile_time_sim_results = wf_model(initial_farm.wt_x, initial_farm.wt_y, wd=chunk_wd, ws=chunk_ws, time=chunk_times, TI=0.1)
            chunk_aep_normalized = float(mobile_time_sim_results.aep(normalize_probabilities=True).sum()) * len(chunk)/len(time_stamps)
            chunk_aeps.append(chunk_aep_normalized)
        else:
            print(f'shifting farm {fast}m from initial starting points for rapid test on chunk {i} of {len(chunks)}')
            # shift = test_perp_slide(Site, initial_farm, turbine, - dia * width_spacing * 0.3, dia * width_spacing * 0.3, granularity=dia * 0.1, plot=plot, time_series_dir=chunk_wd[0])[1]
            initial_farm.perp_slide(fast, chunk_wd[0])
            shift_distances.append(fast)
            shift_directions.append(chunk_wd[0])
            mobile_time_sim_results = wf_model(initial_farm.wt_x, initial_farm.wt_y, wd=chunk_wd, ws=chunk_ws,
                                               time=chunk_times, TI=0.1)
            norm_hours = len(chunk)
            norm_total_hours = len(time_stamps)
            norm_factor = norm_hours/norm_total_hours
            chunk_aep = float(mobile_time_sim_results.aep().sum())
            chunk_aep_normalized = chunk_aep*norm_factor
            chunk_aeps.append(chunk_aep_normalized)
    breathing_AEP = sum(chunk_aeps)

    # calculate difference between time-series immobile and breathing farms
    upside = breathing_AEP - immobile_AEP
    upside_percent = (breathing_AEP - immobile_AEP) / immobile_AEP * 100
    return upside, upside_percent


def animate_flowmap_time_series(series_data, turbine, farm_width=5, farm_length=5, width_spacing=5, length_spacing=7, mobile=False, out_dir='animation', out_name='animation'):
    [time_stamps, ws, wd, outname] = series_data
    ten_deg_bins = np.linspace(0, 360, 37)
    wind_rose = np.histogram(wd, ten_deg_bins)
    primary_heading = wind_rose[1][wind_rose[0].argmax()]
    # create the site
    Site = SiteFromSeries(series_data)  # , plot=True)
    # create the intial farm
    dia = turbine.diameter()
    initial_farm = WindFarm(generate_layout(farm_length, length_spacing * dia, farm_width, width_spacing * dia,
                                            heading_deg=primary_heading))
    frames = []
    if not mobile:
        for i, wind_speed in enumerate(ws):
            fig = plt.figure()
            print(i)
            wind_direction = wd[i]
            wf_model = PropagateDownwind(Site, turbine, wake_deficitModel=dm.NOJDeficit())
            simulation = wf_model(initial_farm.wt_x, initial_farm.wt_y, wd=wind_direction, ws=wind_speed, TI=0.1)
            flow_map = simulation.flow_map(ws=wind_speed, wd=wind_direction)
            frame = flow_map.plot_wake_map(plot_colorbar=False)
            plt.xlabel('x [m]')
            plt.ylabel('y [m]')
            plt.title('Wake Map for over a time-series')
            plt.savefig(f"{out_dir}/{i}.png")
            frames.append(f'{out_dir}/{i}.png')
            plt.close()
    if mobile:
        chunks = time_chunk(series_data, 12)

    # frames to animation
    with imageio.get_writer(f'{out_dir}/{out_name}.gif', mode='I', duration=0.1) as writer:
        for filename in frames:
            image = imageio.v2.imread(filename)
            writer.append_data(image)
    return None


def main():
    wt = NREL15()
    dia = wt.diameter()
    series_data = read_vortex("WindData/Random/758955.6m_100m_UTC_04.0_ERA5.txt", outname='Spain')
    horns_rev_series = read_vortex("WindData/HornsRev/761517.6m_100m_UTC+02.0_ERA5.txt", outname='HornsRev')
    # chunks, chunk_lengths = time_chunk(series_data, 24*7, mode='no freq')
    # plt.hist(chunk_lengths, np.linspace(0, max(chunk_lengths), 100))
    # print(f'The time series, length {len(series_data[0])} hours, was chunked into {len(chunks)} chunks, of average length {np.mean(chunk_lengths)}')
    plt.show()
    upside, upside_percent = sim_time_series(series_data, wt, fast=dia)
    print(f'upside: {upside}')
    print(f'Which is a {upside_percent}% improvement')
    upside, upside_percent = sim_time_series(series_data, wt)
    print(f'upside: {upside}')
    print(f'Which is a {upside_percent}% improvement')
    print(f'HornsRev: {sim_time_series(horns_rev_series, wt, fast=dia)}')
    # sim_time_series(series_data, wt)
    # animate_flowmap_time_series(series_data, wt)




if __name__ == '__main__':
    main()