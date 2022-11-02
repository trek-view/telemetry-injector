import os,re, sys
from pathlib import Path 

from .mp4 import Mp4Atom

from .camm import get_gpx_data as gpx_camm_data
from .gpmd import get_gpx_data as gpx_gpmd_data

from spatialmedia import metadata_utils

def console(d):
    print(d)

def read_gpx(gpx, metadata):
    gpx_data = None
    if metadata == b'camm':
        gpx_data = gpx_camm_data(gpx)
    if metadata == b'gpmd':
        gpx_data = gpx_gpmd_data(gpx)
    return gpx_data

def create_metadata_atoms(f, data, framerate, metadata):
    new_mp4 = None
    if metadata == b'camm':
        mp4_atoms = Mp4Atom()
        new_mp4 = mp4_atoms.create_camm_metadata_atoms(f, data, framerate)
    if metadata == b'gpmd':
        mp4_atoms = Mp4Atom()
        new_mp4 = mp4_atoms.create_gpmd_metadata_atoms(f, data, framerate)
    return new_mp4

def write_metadata(mp4, gpx, output, metadata):
    framerate = 5
    data = read_gpx(gpx, metadata)
    if data:
        output_video = './temp.mp4'
        with open(mp4, "rb") as f:
            new_mp4 = create_metadata_atoms(f, data, framerate, metadata)
            with open(output_video, "wb") as o:
                new_mp4.resize()
                new_mp4.save(f, o)
                o.close()
                #spatialmedia
                metadata = metadata_utils.Metadata()
                metadata.video = metadata_utils.generate_spherical_xml("none", False)
                print(metadata.video)
                metadata_utils.inject_metadata(output_video, output, metadata,
                                                console)
                os.remove(output_video)
