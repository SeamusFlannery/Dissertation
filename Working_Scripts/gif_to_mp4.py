# animation files were too large to easily share, git, or display, so I built this to go and make any gifs into mp4s I could use instead


import moviepy.editor as mp
import os
import glob


def make_mp4(path, path_no_ext):
    clip = mp.VideoFileClip(f'{path}')
    clip.write_videofile(f'{path_no_ext}.mp4')


def find_gifs_make_mp4s(directory):
    gif_files = []
    gif_files_no_ext = []

    # Walk through the directory and all subdirectories
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.gif'):
                full_path = os.path.join(root, file)
                gif_files.append(full_path)
                gif_files_no_ext.append(os.path.splitext(full_path)[0])
    for i in range(len(gif_files)):
        make_mp4(gif_files[i], gif_files_no_ext[i])


find_gifs_make_mp4s(os.getcwd())





