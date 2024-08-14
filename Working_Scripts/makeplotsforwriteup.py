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
                                               dir_sensitivity=10, windrose=False, start=0, end=-1):
    if not os.path.exists(f'{out_dir}'):
        # Create the directory if it does not exist
        os.makedirs(f'{out_dir}')
    # Process the input data to generate primary heading, site, and windrose
    [time_stamps, ws, wd, outname] = series_data
    ten_deg_bins = np.linspace(0, 360, 37)
    wind_rose = np.histogram(wd, ten_deg_bins)
    primary_heading = wind_rose[1][wind_rose[0].argmax()]
    # create the site
    Site = SiteFromSeries(series_data)  # , plot=True)
    if windrose:
        Site.plot_wd_distribution(n_wd=24, ws_bins=[0, 5, 10, 15, 20, 25])
        plt.savefig(f"{out_dir}/windrose.png")
        plt.close()
    # create the intial farm
    dia = turbine.diameter()
    initial_farm = WindFarm(generate_layout(farm_length, length_spacing * dia, farm_width, width_spacing * dia,
                                            heading_deg=primary_heading))
    # trim data to start and endpoints if necessary
    if start != 0 or end != -1:
        short_data = np.array(series_data[0:3]).T[start:end].T.tolist()
        short_data.append([series_data[3]])
        short_data = np.array(short_data, dtype="object")
        series_data = short_data
        [time_stamps, ws, wd, outname] = series_data
    time_stamps = np.array(time_stamps)  # necessary line to make a later np.where() work properly - will not work on lists with single items
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
            plt.xlim(-2000, 10000)
            plt.ylim(-1000, 8000)
            plt.title('Wake Map for over a time-series')
            plt.savefig(f"{out_dir}/{i}.png")
            frames = np.append(frames, f'{out_dir}/{i}.png')
            plt.close()
    if mobile:
        wf_model = PropagateDownwind(Site, turbine, wake_deficitModel=dm.NOJDeficit())
        # simulate time-series with immobile farm
        immobile_time_sim_results = wf_model(initial_farm.wt_x, initial_farm.wt_y, wd=wd, ws=ws, time=time_stamps,
                                             TI=0.1)
        # simulate time-series with breathing farm
        chunks, chunk_lengths = time_chunk(series_data, 20, dir_sensitivity=dir_sensitivity, mode='no freq')
        print(f'{len(chunks)} chunks defined')
        shift_distances = []
        shift_directions = []
        hour = 0
        for i, chunk in enumerate(
                chunks):  # this could be time/computation expensive, consider switching to indexed instead of time-stamp search
            test1 = chunk[0]
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
                hour += 1
                print(f'generating hour {hour}')
                # generate flowmaps
                mobile_time_sim_results = wf_model(initial_farm.wt_x, initial_farm.wt_y, wd=chunk_wd[j], ws=chunk_ws[j],
                                                   time=chunk_times[j], TI=0.1)
                flow_map = mobile_time_sim_results.flow_map(ws=chunk_ws[j], wd=chunk_wd[j])
                frame = flow_map.plot_wake_map(plot_colorbar=False, levels=100)
                # add consistent labelling and axes limits to flowmaps
                plt.xlabel('x [m]')
                plt.ylabel('y [m]')
                plt.xlim(-5000, 6500)
                plt.ylim(1500, 8000)
                plt.title(f'Wake Map for a time-series, position {i}, hour {hour} of {len(time_stamps)}')
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
    horns_rev_series = read_vortex("WindData/HornsRev/761517.6m_100m_UTC+02.0_ERA5.txt", outname='HornsRev')

    animate_flowmap_hardcoded_axes_time_series(horns_rev_series, wt, mobile=True, out_dir='hardcoded plots3', out_name='animation', lookup_table='hornsrev5x5_lookup.csv', dir_sensitivity=1, windrose=True, start=8, end=12)


if __name__ == '__main__':
    main()
