# Seamus Flannery, Sustainable Energy Systems M.Sc., Thesis Code Submission
This GitHub repository contains all the code work and spreadsheets for my Master's thesis on dynamically repositioning floating wind turbines.

The core files are:    
analysis.py - handled uncertainty testing  
Stationholding.py - handles static farms  
TimeSeriesSim.py - handles dynamic farms  

The data structure files are:  
lookup_table.py - saves optimal shift values in a lookup table for computational ease  
North_Wind.py - a file which holds a hardcoded site object that blows north wind on a farm  
p_ct_curves.py - holds the power and thrust coefficient vs wind speed curves for the turbine models used in the thesis  
sites.py - holds hardcoded sites and a flexible time series-to-site object method/class  
turbines.py - holds the data structures for turbine objects

The support files are:  
combine_images.py - adds wind roses to animations  
coordinate_stuff.py - outputs farm coordinates in UTM for use in Velosco NPV software  
gif_to_mp4.py - handles animation file compression  
makeplotsforwriteup.py - prettier plots for the thesis writeup  


The files which were used to learn PyWake and are not used in simulation at all are:  
plot_sites.py - tutorial file on plotting site objects and wake maps  
Time Series Tutorials.py - tutorial file  
Tut_four_turbine_obj.py - tutorial file
Tut_one_basic_plots.py - tutorial file
Tut_three_XRSite_obj.py - tutorial file
Tut_two_site_obj.py - tutorial file

Also included in this repository are the spreadsheets used for financial calculations: "Finance and CapEx, Velosco Validated.xlsx" as well as the lookup table csv files, time series data files (WindData directory), and a number of animation directories which contain all wake map pngs used to generate an animation and the output mp4 file.  
The "plots" directory no longer contains anything particularly useful, but there are niche tidbits which may be of interest to the most avid of dynamic farm enthusiasts