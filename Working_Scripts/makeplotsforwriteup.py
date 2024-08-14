import os

import imageio
import numpy as np
from matplotlib import pyplot as plt
from py_wake.wind_farm_models import PropagateDownwind
from py_wake import deficit_models as dm
from Working_Scripts.Stationholding import WindFarm, generate_layout
from Working_Scripts.TimeSeriesSim import time_chunk
from Working_Scripts.combine_images import combine_images_side_by_side
from Working_Scripts.lookup_table import read_lookup, gen_lookup
from Working_Scripts.sites import SiteFromSeries, read_vortex
import moviepy.editor as mp

from Working_Scripts.turbines import NREL15


def animate_flowmap_hardcoded_axes_time_series(series_data, turbine, farm_width=5, farm_length=5, width_spacing=5,
                                               length_spacing=7,
                                               mobile=False, out_dir='animation', out_name='animation', lookup_table='',
                                               dir_sensitivity=10, windrose=False):
    if not os.path.exists(f'{out_dir}'):
        # Create the directory if it does not exist
        os.makedirs(f'{out_dir}')
    [time_stamps, ws, wd, outname] = series_data
    time_stamps = np.array(time_stamps)
    ten_deg_bins = np.linspace(0, 360, 37)
    wind_rose = np.histogram(wd, ten_deg_bins)
    primary_heading = wind_rose[1][wind_rose[0].argmax()]
    # create the site
    Site = SiteFromSeries(series_data)  # , plot=True)
    if windrose:
        Site.plot_wd_distribution(n_wd=24, ws_bins=[0, 5, 10, 15, 20, 25])
        plt.savefig(f"{out_dir}/windrose.png")
        plt.clf()
    # create the intial farm
    dia = turbine.diameter()
    initial_farm = WindFarm(generate_layout(farm_length, length_spacing * dia, farm_width, width_spacing * dia,
                                            heading_deg=primary_heading))
    frames = np.empty(0)
    if not mobile:
        for i, wind_speed in enumerate(ws):
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
        left, right, bot, top = -2000, 8000, 0, 12000
        hour = 0
        for i, chunk in enumerate(
                chunks): # this could be time/computation expensive, consider switching to indexed instead of time-stamp search
            test = chunk[0]
            test2 = np.where(time_stamps == chunk[0])
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
                fig = plt.figure()
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
    if windrose:
        for filename in frames:
            combine_images_side_by_side(filename, f"{out_dir}/windrose.png", filename)
    with imageio.get_writer(f'{out_dir}/{out_name}.gif', mode='I', duration=0.2) as writer:
        for filename in frames:
            image = imageio.v2.imread(filename)
            writer.append_data(image)
    np.savetxt(f'{out_dir}/{out_name}.gif_frame_list.csv', frames, fmt='%s', delimiter=',')
    clip = mp.VideoFileClip(f'{out_dir}/{out_name}.gif')
    clip.write_videofile(f'{out_dir}/{out_name}.mp4')
    os.remove(f'{out_dir}/{out_name}.gif')
    return None


def main():
    wt = NREL15()
    dia = wt.diameter()
    chile_series = read_vortex("WindData/Chile/758955.6m_100m_UTC_04.0_ERA5.txt", outname='Chile')
    chile_short = np.array(chile_series[0:3]).T[0:25].T.tolist()
    chile_short.append([chile_series[3]])
    chile_short = np.array(chile_short, dtype="object")
    animate_flowmap_hardcoded_axes_time_series(chile_short, wt, mobile=True, out_dir='Chile_hardcoded_axes', out_name='animation', lookup_table='chile5x5_lookup.csv', dir_sensitivity=1, windrose=True)


if __name__ == '__main__':
    main()
