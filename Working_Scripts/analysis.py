# this file written by Seamus Flannery
# this file was designed to give me a space to do some statistical analysis/uncertainty analysis on my initial results
# for dynamic farms, without cluttering my main dynamic farm file "TimeSeriesSim.py"
from TimeSeriesSim import *


# essentially a hardcoded main to probe my results using the uncertainty from Vortex validation docs.
# Compares the AEP uplift in the normal dynamic farm to one with 2% elevated wind speeds and outputs these
# AEPs and the uplifts %'s so I can put them into excel and plot error bars.
def analysis_procedure():
    wt = NREL15()
    dia = wt.diameter()
    sensitivity_settings = [90]
    # sensitivity_settings = [1, 5, 10, 20, 40, 90]
    # bias = 0.38  # vortex validation
    # bias_stdv = 0.32  # vortex validation
    # r_squared_mean = 0.85 # vortex validation
    ws_uncert = 1.02  # vortex validation and industry practice from Velosco

    # READ IN VORTEX DATA, CREATE NOISY VERSIONS
    chile_series = read_vortex("WindData/Chile/758955.6m_100m_UTC_04.0_ERA5.txt", outname='Chile')
    chile_noise = add_noise(chile_series, ws_uncert)
    horns_rev_series = read_vortex("WindData/HornsRev/761517.6m_100m_UTC+02.0_ERA5.txt", outname='HornsRev')
    horns_rev_noise = add_noise(horns_rev_series, ws_uncert)
    # horns_rev_short = read_vortex("WindData/HornsRev/761517.6m_100m_UTC+02.0_ERA5_short.txt", outname='HornsRevShort')
    taiwan_series = read_vortex("WindData/Taiwan/764811.6m_100m_UTC+08.0_ERA5.txt", outname="Taiwan")
    taiwan_noise = add_noise(taiwan_series, ws_uncert)
    nz_series = read_vortex("WindData/New_Zealand/764813.6m_100m_UTC+12.0_ERA5.txt", outname="New Zealand")
    nz_noise = add_noise(nz_series, ws_uncert)
    cali_series = read_vortex('WindData/California/764815.6m_100m_UTC-07.0_ERA5.txt', outname="California")
    cali_noise = add_noise(cali_series, ws_uncert)
    upsides = []
    uncert_upsides = []
    uncertainties = []
    # RUN SITES
    for i, sensitivity_setting in enumerate(sensitivity_settings):
        print('Chile Site:')
        upside, upside_percent, initial_farm, extreme_farm = sim_time_series_lookup(chile_series, wt, fast='lookup',
                                                                                    lookup_file='chile5x5_lookup.csv',
                                                                                    chunk_sensitivity=sensitivity_setting)
        print(f'upside: {str(upside)[0:5]} GWh')
        print(f'Which is a {str(upside_percent)[0:5]}% improvement')
        uncert_upside, uncert_percent, initial_farm, extreme_farm = sim_time_series_lookup(chile_noise, wt,
                                                                                           fast='lookup',
                                                                                           lookup_file='chile5x5_lookup.csv',
                                                                                           chunk_sensitivity=sensitivity_setting)
        print(
            f'uncertainty upside, {uncert_percent}%, vs initial upside {upside_percent}% for a percent uncertainty of {(upside_percent - uncert_percent) * 100 / upside_percent}\n%')
        upsides.append(upside_percent)
        uncert_upsides.append(uncert_percent)
        uncertainties.append((upside_percent - uncert_percent) * 100 / upside_percent)
        ##################################
        print('Hornsrev Site:')
        upside, upside_percent, initial_farm, extreme_farm = sim_time_series_lookup(horns_rev_series, wt, fast='lookup',
                                                                                    lookup_file='hornsrev5x5_lookup.csv',
                                                                                    chunk_sensitivity=sensitivity_setting)
        print(f'upside: {str(upside)[0:5]} GWh')
        print(f'Which is a {str(upside_percent)[0:5]}% improvement')
        uncert_upside, uncert_percent, initial_farm, extreme_farm = sim_time_series_lookup(horns_rev_noise, wt,
                                                                                           fast='lookup',
                                                                                           lookup_file='hornsrev5x5_lookup.csv',
                                                                                           chunk_sensitivity=sensitivity_setting)
        print(
            f'uncertainty upside, {uncert_percent}%, vs initial upside {upside_percent}% for a percent uncertainty of {(upside_percent - uncert_percent) * 100 / upside_percent}%\n')
        upsides.append(upside_percent)
        uncert_upsides.append(uncert_percent)
        uncertainties.append((upside_percent - uncert_percent) * 100 / upside_percent)
        ##################################
        print('New Zealand Site:')
        upside, upside_percent, initial_farm, extreme_farm = sim_time_series_lookup(nz_series, wt, fast='lookup',
                                                                                    lookup_file='nz5x5_lookup.csv',
                                                                                    chunk_sensitivity=sensitivity_setting)
        print(f'upside: {str(upside)[0:5]} GWh')
        print(f'Which is a {str(upside_percent)[0:5]}% improvement')
        uncert_upside, uncert_percent, initial_farm, extreme_farm = sim_time_series_lookup(nz_noise, wt,
                                                                                           fast='lookup',
                                                                                           lookup_file='nz5x5_lookup.csv',
                                                                                           chunk_sensitivity=sensitivity_setting)
        print(
            f'uncertainty upside, {uncert_percent}%, vs initial upside {upside_percent}% for a percent uncertainty of {(upside_percent - uncert_percent) * 100 / upside_percent}%\n')
        upsides.append(upside_percent)
        uncert_upsides.append(uncert_percent)
        uncertainties.append((upside_percent - uncert_percent) * 100 / upside_percent)
        ##################################
        print('California Site:')
        upside, upside_percent, initial_farm, extreme_farm = sim_time_series_lookup(cali_series, wt, fast='lookup',
                                                                                    lookup_file='cali5x5_lookup.csv',
                                                                                    chunk_sensitivity=sensitivity_setting)
        print(f'upside: {str(upside)[0:5]} GWh')
        print(f'Which is a {str(upside_percent)[0:5]}% improvement')
        uncert_upside, uncert_percent, initial_farm, extreme_farm = sim_time_series_lookup(cali_noise, wt,
                                                                                           fast='lookup',
                                                                                           lookup_file='cali5x5_lookup.csv',
                                                                                           chunk_sensitivity=sensitivity_setting)
        print(
            f'uncertainty upside, {uncert_percent}%, vs initial upside {upside_percent}% for a percent uncertainty of {(upside_percent - uncert_percent) * 100 / upside_percent}%\n')
        upsides.append(upside_percent)
        uncert_upsides.append(uncert_percent)
        uncertainties.append((upside_percent - uncert_percent) * 100 / upside_percent)
        ##################################
        print('Taiwan Site:')
        upside, upside_percent, initial_farm, extreme_farm = sim_time_series_lookup(taiwan_series, wt, fast='lookup',
                                                                                    lookup_file='taiwan5x5_lookup.csv',
                                                                                    chunk_sensitivity=sensitivity_setting)
        print(f'upside: {str(upside)[0:5]} GWh')
        print(f'Which is a {str(upside_percent)[0:5]}% improvement')
        uncert_upside, uncert_percent, initial_farm, extreme_farm = sim_time_series_lookup(taiwan_noise, wt,
                                                                                           fast='lookup',
                                                                                           lookup_file='taiwan5x5_lookup.csv',
                                                                                           chunk_sensitivity=sensitivity_setting)
        print(
            f'uncertainty upside, {uncert_percent}%, vs initial upside {upside_percent}% for a percent uncertainty of {(upside_percent - uncert_percent) * 100 / upside_percent}%\n')
        upsides.append(upside_percent)
        uncert_upsides.append(uncert_percent)
        uncertainties.append((upside_percent - uncert_percent) * 100 / upside_percent)
    np.savetxt("Excel_inputs.csv", [upsides, uncert_upsides, uncertainties], delimiter=',')
    return [upsides, uncert_upsides, uncertainties]


def main():
    analysis_procedure()


if __name__ == '__main__':
    main()
