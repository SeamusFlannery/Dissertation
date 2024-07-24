# need this to reformat my gifs
# may expand this to support gifs with a windrose in the corner,
# a time-series conducive wind arrow, and a dashboard on turbine spacing, per Scott's suggestion
# NOT CURRENTLY WORKING AT ALL
import aspose.words as aw
import os
import imageio
import pathlib

# get list of pngs
path = str(pathlib.Path().resolve())
filenames = os.listdir(f'{path}/mobile_animation')
filenames.sort()
filenames = filenames[0:len(filenames)-1]
out_dir = 'mobile_animation'
out_name = 'test.gif'
with imageio.get_writer(f'{out_dir}/{out_name}.gif', mode='I', duration=0.2) as writer:
    for filename in filenames:
        image = imageio.v2.imread(filename)
        writer.append_data(image)


