import numpy as np
import matplotlib.pyplot as plt
from Stationholding import generate_layout, WindFarm, Turbine_instance, find_opt_shift, test_perp_slide
from turbines import NREL15
from sites import MyBiSite, MyTriSite, EastBlowHornsrevSite, SiteFromSeries, read_vortex
from py_wake.wind_farm_models import PropagateDownwind
from py_wake import deficit_models as dm
from lookup_table import gen_lookup, read_lookup
import imageio
import warnings
from coordinate_stuff import farm_to_utm, dms_to_decimal
import copy

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
            elif abs(dom_wind_dir - wd[
                i]) <= dir_sensitivity:  # default if wind direction is within 30, no repositioning necessary?
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
            if abs(dom_wind_dir - wd[
                i]) <= dir_sensitivity:  # default if wind direction is within 30, no repositioning necessary?
                current_chunk.append(timestamp)
            elif abs(dom_wind_dir - wd[i]) > dir_sensitivity:
                chunks.append(current_chunk)
                chunk_lengths.append(len(current_chunk))
                dom_wind_dir = wd[i]
                current_chunk = [timestamp]
        return chunks, chunk_lengths


def sim_time_series(series_data, turbine, farm_width=5, farm_length=5, width_spacing=5, length_spacing=7, plot=False,
                    fast=''):
    # start by analyzing the input time_series
    [time_stamps, ws, wd, outname] = series_data
    print(f'Beginning analysis of {outname}')
    ten_deg_bins = np.linspace(0, 360, 37)
    wind_rose = np.histogram(wd, ten_deg_bins)
    primary_heading = wind_rose[1][wind_rose[0].argmax()]
    # create the site
    Site = SiteFromSeries(series_data, plot=True)  # , plot=True)
    # create the initial farm
    dia = turbine.diameter()
    target_aep, shift, initial_farm = find_opt_shift(Site, turbine, farm_width, farm_length, width_spacing,
                                                     length_spacing, heading_deg=primary_heading, plot=plot)
    # initial_farm = WindFarm(generate_layout(farm_length, length_spacing*dia, farm_width, width_spacing*dia, heading_deg=primary_heading))
    wf_model = PropagateDownwind(Site, turbine, wake_deficitModel=dm.NOJDeficit())
    # simulate time-series with immobile farm
    immobile_time_sim_results = wf_model(initial_farm.wt_x, initial_farm.wt_y, wd=wd, ws=ws, time=time_stamps, TI=0.1)
    immobile_AEP = float(immobile_time_sim_results.aep_ilk(normalize_probabilities=False).sum())
    # TODO figure out what method I can use that will actually calculate the AEP for a farm according only to the time series given (as below)
    immobile_time_sim_results_test2 = wf_model(initial_farm.wt_x, initial_farm.wt_y, wd=wd[0:100], ws=ws[0:100],
                                               time=time_stamps[0:100], TI=0.1)
    immobile_AEP_test2 = float(immobile_time_sim_results.aep_ilk(normalize_probabilities=False).sum())
    # simulate time-series with breathing farm
    chunks, chunk_lengths = time_chunk(series_data, 20, mode='no freq')
    print(f'{len(chunks)} chunks defined')
    shift_distances = []
    shift_directions = []
    chunk_aeps = []  # TODO are these normalizeD?
    for i, chunk in enumerate(
            chunks):  # this could be time/computation expensive, consider switching to indexed instead of time-stamp search
        start_index = np.where(time_stamps == chunk[0])[0][0]
        end_index = start_index + chunk_lengths[i]
        chunk_times = time_stamps[start_index:end_index]
        chunk_wd = wd[start_index:end_index]
        chunk_ws = ws[start_index:end_index]
        if fast == '':
            print(f'testing for optimal responsive farm shift on chunk {i} of {len(chunks)}')
            shift = test_perp_slide(Site, initial_farm, turbine, - dia * width_spacing * 0.3, dia * width_spacing * 0.3,
                                    granularity=dia * 0.1, plot=plot, time_series_dir=chunk_wd[0])[1]
            initial_farm.perp_slide(shift, chunk_wd[0])
            shift_distances.append(shift)
            shift_directions.append(chunk_wd[0])
            mobile_time_sim_results = wf_model(initial_farm.wt_x, initial_farm.wt_y, wd=chunk_wd, ws=chunk_ws,
                                               time=chunk_times, TI=0.1)
            chunk_aep_normalized = float(mobile_time_sim_results.aep(normalize_probabilities=True).sum()) * len(
                chunk) / len(time_stamps)
            chunk_aeps.append(chunk_aep_normalized)
        else:
            # print(f'shifting farm {fast}m from initial starting points for rapid test on chunk {i} of {len(chunks)}')
            # shift = test_perp_slide(Site, initial_farm, turbine, - dia * width_spacing * 0.3, dia * width_spacing * 0.3, granularity=dia * 0.1, plot=plot, time_series_dir=chunk_wd[0])[1]
            initial_farm.perp_slide(fast, chunk_wd[0])
            shift_distances.append(fast)
            shift_directions.append(chunk_wd[0])
            mobile_time_sim_results = wf_model(initial_farm.wt_x, initial_farm.wt_y, wd=chunk_wd, ws=chunk_ws,
                                               time=chunk_times, TI=0.1)
            norm_hours = len(chunk)
            norm_total_hours = len(time_stamps)
            norm_factor = norm_hours / norm_total_hours
            chunk_aep = float(mobile_time_sim_results.aep().sum())
            chunk_aep_normalized = chunk_aep * norm_factor
            chunk_aeps.append(chunk_aep_normalized)
    breathing_AEP = sum(chunk_aeps)

    # calculate difference between time-series immobile and breathing farms
    upside = breathing_AEP - immobile_AEP
    upside_percent = (breathing_AEP - immobile_AEP) / immobile_AEP * 100
    return upside, upside_percent


# virtually a copy of sim_time_series but incorporates the generation/usage of a lookup table for the given initial farm/site combination
def sim_time_series_lookup(series_data, turbine, farm_width=5, farm_length=5, width_spacing=5, length_spacing=7,
                           plot=False, fast='', lookup_file='', chunk_freq=20, chunk_sensitivity=20):
    # start by analyzing the input time_series
    [time_stamps, ws, wd, outname] = series_data
    # print(f'Beginning analysis of {outname}')
    ten_deg_bins = np.linspace(0, 360, 37)
    wind_rose = np.histogram(wd, ten_deg_bins)
    primary_heading = wind_rose[1][wind_rose[0].argmax()]
    # create the site
    Site = SiteFromSeries(series_data, plot=plot)  # , plot=True)
    # create the initial farm
    dia = turbine.diameter()
    target_aep, shift, initial_farm = find_opt_shift(Site, turbine, farm_width, farm_length, width_spacing,
                                                     length_spacing, heading_deg=primary_heading, plot=plot)
    extreme_farm = copy.deepcopy(initial_farm)
    # initial_farm = WindFarm(generate_layout(farm_length, length_spacing*dia, farm_width, width_spacing*dia, heading_deg=primary_heading))
    wf_model = PropagateDownwind(Site, turbine, wake_deficitModel=dm.NOJDeficit())
    # simulate time-series with immobile farm
    immobile_time_sim_results = wf_model(initial_farm.wt_x, initial_farm.wt_y, wd=wd, ws=ws, time=time_stamps, TI=0.1)
    immobile_AEP = float(immobile_time_sim_results.aep_ilk(normalize_probabilities=False).sum())
    # TODO figure out what method I can use that will actually calculate the AEP for a farm according only to the time series given (as below)
    immobile_time_sim_results_test2 = wf_model(initial_farm.wt_x, initial_farm.wt_y, wd=wd[0:100], ws=ws[0:100],
                                               time=time_stamps[0:100], TI=0.1)
    immobile_AEP_test2 = float(immobile_time_sim_results.aep_ilk(normalize_probabilities=False).sum())
    # simulate time-series with breathing farm
    chunks, chunk_lengths = time_chunk(series_data, chunk_freq, dir_sensitivity=chunk_sensitivity, mode='no freq')
    print(f'{len(chunks)} chunks defined')
    shift_distances = []
    shift_directions = []
    chunk_aeps = []
    if fast == 'lookup':
        try:
            degrees, shift_table = read_lookup(lookup_file)
        except FileNotFoundError:
            degrees, shift_table = gen_lookup(Site, initial_farm, turbine, outname=lookup_file)
        lookup_table = np.array([degrees, shift_table])
    for i, chunk in enumerate(
            chunks):  # this could be time/computation expensive, consider switching to indexed instead of time-stamp search
        start_index = np.where(time_stamps == chunk[0])[0][0]
        end_index = start_index + chunk_lengths[i]
        chunk_times = time_stamps[start_index:end_index]
        chunk_wd = wd[start_index:end_index]
        chunk_ws = ws[start_index:end_index]
        if fast == '':
            print(f'testing for optimal responsive farm shift on chunk {i} of {len(chunks)}')
            shift = test_perp_slide(Site, initial_farm, turbine, - dia * width_spacing * 0.3, dia * width_spacing * 0.3,
                                    granularity=dia * 0.1, plot=plot, time_series_dir=chunk_wd[0])[1]
            initial_farm.perp_slide(shift, chunk_wd[0])
            shift_distances.append(shift)
            shift_directions.append(chunk_wd[0])
            mobile_time_sim_results = wf_model(initial_farm.wt_x, initial_farm.wt_y, wd=chunk_wd, ws=chunk_ws,
                                               time=chunk_times, TI=0.1)
            chunk_aep_normalized = float(mobile_time_sim_results.aep(normalize_probabilities=True).sum()) * len(
                chunk) / len(time_stamps)
            chunk_aeps.append(chunk_aep_normalized)

        elif fast == 'lookup':
            slide_dist = lookup_table[1, np.where(lookup_table[0] == chunk_wd[0])]
            # print(f'shifting farm {int(slide_dist)} m from initial starting points for rapid test on chunk {i} of {len(chunks)}')
            slide_perp_angle = chunk_wd[0]
            initial_farm.perp_slide(slide_dist, slide_perp_angle)
            shift_distances.append(slide_dist)
            shift_directions.append(chunk_wd[0])
            mobile_time_sim_results = wf_model(initial_farm.wt_x, initial_farm.wt_y, wd=chunk_wd, ws=chunk_ws,
                                               time=chunk_times, TI=0.1)
            norm_hours = len(chunk)
            norm_total_hours = len(time_stamps)
            norm_factor = norm_hours / norm_total_hours
            chunk_aep = float(mobile_time_sim_results.aep().sum())
            chunk_aep_normalized = chunk_aep * norm_factor
            chunk_aeps.append(chunk_aep_normalized)
    breathing_AEP = sum(chunk_aeps)
    # calculate difference between time-series immobile and breathing farms
    upside = breathing_AEP - immobile_AEP
    upside_percent = (breathing_AEP - immobile_AEP) / immobile_AEP * 100
    # find extreme farm shift
    max_slide = int(max(shift_distances))
    max_slide_dir = shift_directions[shift_distances.index(max_slide)]
    extreme_farm.perp_slide(max_slide, max_slide_dir)
    return upside, upside_percent, initial_farm, extreme_farm


def animate_flowmap_time_series(series_data, turbine, farm_width=5, farm_length=5, width_spacing=5, length_spacing=7,
                                mobile=False, out_dir='animation', out_name='animation', lookup_table='',
                                dir_sensitivity=10):
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
    frames = np.empty(0)
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
            frames = np.append(frames, f'{out_dir}/{i}.png')
            plt.close()
    if mobile:
        ten_deg_bins = np.linspace(0, 360, 37)
        wind_rose = np.histogram(wd, ten_deg_bins)
        primary_heading = wind_rose[1][wind_rose[0].argmax()]
        wf_model = PropagateDownwind(Site, turbine, wake_deficitModel=dm.NOJDeficit())
        # simulate time-series with immobile farm
        immobile_time_sim_results = wf_model(initial_farm.wt_x, initial_farm.wt_y, wd=wd, ws=ws, time=time_stamps,
                                             TI=0.1)
        # simulate time-series with breathing farm
        chunks, chunk_lengths = time_chunk(series_data, 20, dir_sensitivity=dir_sensitivity, mode='no freq')
        print(f'{len(chunks)} chunks defined')
        shift_distances = []
        shift_directions = []
        # generate initial farm map and extract x/ylims
        # flow_map = immobile_time_sim_results.flow_map(ws=7, wd=primary_heading)
        # frame1 = flow_map.plot_wake_map(plot_colorbar=False)
        # plt.savefig(f"{out_dir}/0.png")
        # frames = np.append(frames, f'{out_dir}/0.png')
        # left, right = plt.xlim()
        # left -= 1000
        # bot, top = plt.ylim()
        # top += 400
        left, right, bot, top = -5000, 5000, -2000, 10000
        hour = 0
        for i, chunk in enumerate(
                chunks):  # this could be time/computation expensive, consider switching to indexed instead of time-stamp search
            start_index = np.where(time_stamps == chunk[0])[0][0]
            end_index = start_index + chunk_lengths[i]
            chunk_times = time_stamps[start_index:end_index]
            chunk_wd = wd[start_index:end_index]
            chunk_ws = ws[start_index:end_index]
            if lookup_table == '':
                initial_farm.perp_slide(dia, chunk_wd[0])
                shift_distances.append(dia)
                shift_directions.append(chunk_wd[0])
            else:
                try:
                    degrees, shift = read_lookup(lookup_table)
                except FileNotFoundError:
                    degrees, shift = gen_lookup(Site, initial_farm, turbine, outname=lookup_table)
                shift_index = np.where(degrees == chunk_wd[0])
                initial_farm.perp_slide(shift[shift_index], chunk_wd[0])
                shift_distances.append(shift[shift_index])
                shift_directions.append(chunk_wd[0])
            for j, time in enumerate(chunk):
                hour += 1
                print(f'generating hour {hour}')
                # generate flowmaps
                mobile_time_sim_results = wf_model(initial_farm.wt_x, initial_farm.wt_y, wd=chunk_wd[j], ws=chunk_ws[j],
                                                   time=chunk_times[j], TI=0.1)
                flow_map = mobile_time_sim_results.flow_map(ws=chunk_ws[j], wd=chunk_wd[j])
                frame = flow_map.plot_wake_map(plot_colorbar=False)
                # add consistent labelling and axes limits to flowmaps
                plt.xlabel('x [m]')
                plt.ylabel('y [m]')
                plt.title(f'Wake Map for over a time-series, position {i}, hour {hour} of {len(time_stamps)}')
                plt.xlim((left, right))
                plt.ylim((bot, top))
                # save flowmaps
                plt.savefig(f"{out_dir}/{hour}.png")
                frames = np.append(frames, f'{out_dir}/{hour}.png')
                plt.close()
            print(f'{len(chunk)} frames/hours generated for position {i} of {len(chunks)}')
    # frames to animation
    with imageio.get_writer(f'{out_dir}/{out_name}.gif', mode='I', duration=0.2) as writer:
        for filename in frames:
            image = imageio.v2.imread(filename)
            writer.append_data(image)
    np.savetxt(f'{out_dir}/{out_name}.gif_frame_list.csv', frames, fmt='%s', delimiter=',')
    return None


def add_noise(series_data, ws_uncert):
    ws = series_data[1]
    # noise = np.random.normal(noise_mean, noise_stdv, len(ws))
    ws_w_noise = [x*ws_uncert for x in ws]
    series_data = [series_data[0], ws_w_noise, series_data[2], series_data[3]]
    return series_data


def main():
    wt = NREL15()
    dia = wt.diameter()
    sensitivity_settings = [1, 5, 10, 20, 40, 90]
    # bias = 0.38  # vortex validation
    # bias_stdv = 0.32  # vortex validation
    # r_squared_mean = 0.85 # vortex validation
    ws_uncert = 1.02  # vortex validation and industry practice from Velosco

    # READ IN VORTEX DATA, CREATE NOISY VERSIONS (Vortex data 0.85 R^2 hourly data -> 2% ws uncertainty)
    chile_series = read_vortex("WindData/Random/758955.6m_100m_UTC_04.0_ERA5.txt", outname='Chile')
    # chile_noise = add_noise(chile_series, ws_uncert)
    horns_rev_series = read_vortex("WindData/HornsRev/761517.6m_100m_UTC+02.0_ERA5.txt", outname='HornsRev')
    # horns_rev_noise = add_noise(horns_rev_series, ws_uncert)
    # # horns_rev_short = read_vortex("WindData/HornsRev/761517.6m_100m_UTC+02.0_ERA5_short.txt", outname='HornsRevShort')
    # taiwan_series = read_vortex("WindData/Taiwan/764811.6m_100m_UTC+08.0_ERA5.txt", outname="Taiwan")
    # taiwan_noise = add_noise(taiwan_series, ws_uncert)
    # nz_series = read_vortex("WindData/New_Zealand/764813.6m_100m_UTC+12.0_ERA5.txt", outname="New Zealand")
    # nz_noise = add_noise(nz_series, ws_uncert)
    # cali_series = read_vortex('WindData/California/764815.6m_100m_UTC-07.0_ERA5.txt', outname="California")
    # cali_noise = add_noise(cali_series, ws_uncert)
    maine_series = read_vortex("WindData/Maine/771051.6m100mUTC-03.0ERA5_FULLYEAR_EDIT.txt", outname='Maine')
    maine_noise = add_noise(maine_series, ws_uncert)

    # RUN SITES
    # wind_rose = SiteFromSeries(maine_series, plot=True)

    for i, sensitivity_setting in enumerate(sensitivity_settings):
         print('Maine Site:')
         upside, upside_percent, initial_farm, extreme_farm = sim_time_series_lookup(maine_series, wt, fast='lookup',
                                                                                     lookup_file='maine5x5_lookup.csv',
                                                                                     chunk_sensitivity=sensitivity_setting)
         print(f'upside: {str(upside)[0:5]} GWh')
         print(f'Which is a {str(upside_percent)[0:5]}% improvement')
         uncert_upside, uncert_percent, initial_farm, extreme_farm = sim_time_series_lookup(maine_noise, wt,
                                                                                            fast='lookup',
                                                                                            lookup_file='maine5x5_lookup.csv',
                                                                                            chunk_sensitivity=sensitivity_setting)
         print(
             f'uncertainty upside, {uncert_percent}%, vs initial upside {upside_percent}% for a percent uncertainty of {(upside_percent - uncert_percent) * 100 / upside_percent}\n%')


    # TURBINE COORDINATE EXTRACTION NOT IN USE CURRENTLY
    # horns_rev_geodetic = [(55, 29, 9.5), (7, 50, 23.9)]  # Lat, Long
    # horns_rev_dec = [dms_to_decimal(horns_rev_geodetic[0]), dms_to_decimal(horns_rev_geodetic[1])]
    #
    chile_dec = [-25, -70]
    # taiwan_dec = [24.67, 120.05]
    # nz_dec = [-37.405074, 178.681641]
    # ca_dec = [33.870416, -120.739746]
    # upside, upside_percent, initial_farm, extreme_farm = sim_time_series_lookup(chile_series, wt, fast='lookup',
    #                                                                              lookup_file='chile5x5_lookup.csv',
    #                                                                              chunk_sensitivity=1)
    # initial_farm_coords = farm_to_utm(initial_farm, chile_dec)
    # extreme_farm_coords = farm_to_utm(extreme_farm, chile_dec)
    # print(f'initial farm coord list: {initial_farm_coords}')
    # print(f'extreme farm coord list: {extreme_farm_coords}')
    # raw_init_coords = np.squeeze(initial_farm_coords[1])
    # raw_extr_coords = np.squeeze(extreme_farm_coords[1])
    # np.savetxt(f"farm_coords/initial_farm_coords.csv", raw_init_coords, delimiter=",")
    # np.savetxt(f"farm_coords/extreme_farm_coords.csv", raw_extr_coords, delimiter=",")

    # print('Taiwan Site:')
    # upside, upside_percent = sim_time_series_lookup(taiwan_series, wt, fast="lookup", lookup_file="taiwan5x5_lookup.csv", plot=False, chunk_sensitivity=1)
    # print(f'upside: {str(upside)[0:5]} GWh')
    # print(f'Which is a {str(upside_percent)[0:5]}% improvement')

    # print('New Zealand Site:')
    # upside, upside_percent = sim_time_series_lookup(nz_series, wt, fast="lookup", lookup_file="nz5x5_lookup.csv", plot=False, chunk_sensitivity=1)
    # print(f'upside: {str(upside)[0:5]} GWh')
    # print(f'Which is a {str(upside_percent)[0:5]}% improvement')

    # print('California Site:')
    # upside, upside_percent = sim_time_series_lookup(cali_series, wt, fast="lookup", lookup_file="cali5x5_lookup.csv", plot=False, chunk_sensitivity=90)
    # print(f'upside: {str(upside)[0:5]} GWh')
    # print(f'Which is a {str(upside_percent)[0:5]}% improvement')

    # ANIMATION CODE NOT CURRENTLY IN USE
    # animate_flowmap_time_series(chile_series, wt, mobile=True, out_dir='chile_mobile_animation_highsense', out_name='animation', lookup_table='chile5x5_lookup.csv', dir_sensitivity=1)
    # chunks, chunk_lengths = time_chunk(series_data, 24*7, mode='no freq')
    # plt.hist(chunk_lengths, np.linspace(0, max(chunk_lengths), 100))
    # print(f'The time series, length {len(series_data[0])} hours, was chunked into {len(chunks)} chunks, of average length {np.mean(chunk_lengths)}')
    # plt.close()


if __name__ == '__main__':
    main()
