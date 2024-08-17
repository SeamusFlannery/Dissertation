# written by Seamus Flannery
# this file was written to turn farm objects output by my simulation scripts into lists of coordinates in UTM
# which could then be used by Velosco software. These were used to determine shift displacements in meters from
# original siting layouts, which was then used for costing mooring line and cables.
import pyproj
import numpy as np


# where dms is degrees minutes seconds tuple
def dms_to_decimal(dms):
    decimal_degrees = dms[0] + (dms[1] / 60) + (dms[2] / 3600)
    return decimal_degrees


# Converts geodetic coordinates (latitude, longitude) to UTM coordinates.
def geodetic_to_utm(lat, lon):

    # Create a transformer object for converting to UTM
    transformer = pyproj.Transformer.from_crs("epsg:4326", "epsg:32633", always_xy=True)

    # Perform the transformation
    easting, northing = transformer.transform(lon, lat)

    # Determine the UTM zone
    zone_number = int((lon + 180) / 6) + 1

    return zone_number, easting, northing


def farm_to_utm(farm, geodetic_duple):
    lat, lon = geodetic_duple[0], geodetic_duple[1]
    zone_number, easting, northing = geodetic_to_utm(lat, lon)
    x_list = [x + easting for x in farm.wt_x]
    y_list = [y + northing for y in farm.wt_y]
    coords_list = np.array([x_list, y_list]).T
    return zone_number, coords_list
