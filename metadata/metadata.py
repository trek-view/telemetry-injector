import os,re, sys, math, json, datetime, subprocess
from pathlib import Path 

import gpxpy
import gpxpy.gpx

from haversine import haversine, Unit
from geographiclib.geodesic import Geodesic

import xml.etree
import xml.etree.ElementTree as ET

from .mp4 import Mp4Atom

from .camm import get_gpx_data as gpx_camm_data
from .gpmd import get_gpx_data as gpx_gpmd_data

from spatialmedia import metadata_utils

def console(d):
    print(d)

def latLngToDecimal(latLng):
    deg, minutes, seconds, direction = re.split('[deg\'"]+', latLng)
    return (float(deg.strip()) + float(minutes.strip())/60 + float(seconds.strip())/(60*60)) * (-1 if direction.strip() in ['W', 'S'] else 1)

def getAltitudeFloat(altitude):
    alt = float(altitude.split(" ")[0])
    return alt

def ffmpeg_video_from_images(images_dir, start_num, frame_rate, mp4_file):
    cmd = [
        'ffmpeg',
        '-y',
        '-r', str(frame_rate),
		"-start_number",
		str(start_num),
        '-vcodec', 'mjpeg',
        '-i', str(images_dir),
        '-vcodec', 'libx264',
        '-pix_fmt', 'yuv420p',
        str(mp4_file)
    ]
    out = subprocess.run(
        cmd,
        capture_output=False
    )

def get_images_metadata(img_dir, fn):
    cmd = [
        "exiftool",
        "-r",
        "-json",
        "-ext",
        "jpg",
        "-fileorder",
        fn,
        img_dir,
    ]
    out = subprocess.run(
        cmd,
        capture_output=True
    )
    json_output = out.stdout.decode('utf-8', 'ignore')
    json_output = json.loads(json_output)
    return json_output

def get_ff_names(path_name):
    path_name = Path(path_name)
    suffix = path_name.suffix
    name = os.path.basename(path_name)
    _name = re.findall('(.*?)([0-9]+)', name)
    start_num = name
    pattern = '%06d.jpg'
    err = True
    if len(_name) == 1:
        _name = list(_name[0])
        if len(_name) > 1:
            start_num = _name[-1]
            _name.remove(start_num)
            _name = ''.join(_name)
            pattern = _name+'%0'+str(len(start_num))+'d'+suffix
            err = False
    return start_num, pattern, err

def create_video_from_images(img_dir, output_dir, output_vid, o_vid, framerate, metadata):
    ms = 100.0/framerate/100.0
    images = {}
    video = None
    output = os.path.join(output_dir, o_vid)
    json_output = get_images_metadata(img_dir, "")
    if len(json_output) < 10:
        print('Atleast 10 images are required.')
        exit()
    suffix = Path(json_output[0]['SourceFile']).suffix
    photo_names = os.path.basename(json_output[0]['SourceFile']).split('_')
    photo_num = photo_names[-1]
    start_num, pattern, err = get_ff_names(os.path.basename(json_output[0]['SourceFile']))
    if err:
        print('Image file name has no proper sequence. Please make sure images are in sequence and has ascending numbering (00001, 00002..., 00008) etc.')
        exit()
    print('start_num, pattern', start_num, pattern)
    if len(photo_names) > 1:
        photo_names.remove(photo_num)
        print(photo_names)
        basename = '_'.join(photo_names)
        video = os.path.join(output_dir, 'basename.mp4')
        v_path = os.path.join(img_dir, pattern)
        print('=>', v_path, video, start_num)
        ffmpeg_video_from_images(v_path, start_num, 5, video)
    else:
        video = os.path.join(output_dir, 'basename.mp4')
        v_path = os.path.join(img_dir, pattern)
        print('=>', v_path)
        ffmpeg_video_from_images(v_path, start_num, 5, video)
        basename = json_output[0]['SourceFile'].split(os.sep)[-2]
    
    for img in json_output:
        images[os.path.basename(img['SourceFile'])] = img
    gpx = gpxpy.gpx.GPX()
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)
    keys = list(images.keys())
    keys.sort()

    m = json_output[0]['GPSDateTime'].split('.')
    if len(m) < 2:
        json_output[0]['GPSDateTime'] = json_output[0]['GPSDateTime'].replace('Z', '') + '.000Z'
    timestamp = datetime.datetime.strptime(json_output[0]['GPSDateTime'].replace(' ', 'T'), '%Y:%m:%dT%H:%M:%S.%fZ')

    i = 0
    for k in keys:
        g = images[k]
        start_latitude = latLngToDecimal(g['GPSLatitude'])
        start_longitude = latLngToDecimal(g['GPSLongitude'])
        start_altitude = getAltitudeFloat(g['GPSAltitude'])
        if i < (len(keys)-1):
            g_next = images[keys[i+1]]
            m = g_next['GPSDateTime'].split('.')
            if len(m) < 2:
                g_next['GPSDateTime'] = g_next['GPSDateTime'].replace('Z', '') + '.000Z'
            timestamp_next = datetime.datetime.strptime(g_next['GPSDateTime'].replace(' ', 'T'), '%Y:%m:%dT%H:%M:%S.%fZ')
            time_diff = (timestamp_next-timestamp).total_seconds()

            end_latitude = latLngToDecimal(g_next['GPSLatitude'])
            end_longitude = latLngToDecimal(g_next['GPSLongitude'])
            end_altitude = getAltitudeFloat(g_next['GPSAltitude'])
            
            distance = haversine((start_latitude, start_longitude), (end_latitude, end_longitude), Unit.METERS)

            brng = Geodesic.WGS84.Inverse(start_latitude, start_longitude, end_latitude, end_longitude)
            azimuth1 = (brng['azi1'] + 360) % 360
            azimuth2 = (brng['azi2'] + 360) % 360
            AC = math.sin(math.radians(azimuth1))*distance
            BC = math.cos(math.radians(azimuth2))*distance
            alt = end_altitude - start_altitude
            if time_diff > 0:
                v_east = AC/time_diff
                v_north = BC/time_diff
                v_up = alt/time_diff
            else:
                v_east = 0.5
                v_north = 0.5
                v_up = 0
        else:
            v_east = 0.5
            v_north = 0.5
            v_up = 0

        gpx_point = gpxpy.gpx.GPXTrackPoint(
            start_latitude, 
            start_longitude, 
            elevation=getAltitudeFloat(g['GPSAltitude']), 
            time=timestamp)
        el = ET.Element(f'HorizontalAccuracy')
        el.text = str(1.0)
        gpx_point.extensions.append(el)
        el = ET.Element(f'VerticalAccuracy')
        el.text = str(1.0)
        gpx_point.extensions.append(el)
        el = ET.Element(f'VelocityEast')
        el.text = str(v_east)
        gpx_point.extensions.append(el)
        el = ET.Element(f'VelocityNorth')
        el.text = str(v_north)
        gpx_point.extensions.append(el)
        el = ET.Element(f'VelocityUp')
        el.text = str(v_up)
        gpx_point.extensions.append(el)
        el = ET.Element(f'SpeedAccuracy')
        el.text = str(0)
        gpx_point.extensions.append(el)
        timestamp = timestamp+datetime.timedelta(0, ms)
        gpx_segment.points.append(gpx_point)
        i += 1
    gpx_path = os.path.join(output_dir, '{}.gpx'.format(basename))
    with open(gpx_path, "w") as f:
        f.write(gpx.to_xml())
    if metadata == b'camm':
        write_metadata(video, gpx_path, output, framerate, b'camm')
    if metadata == b'gpmd':
        write_metadata(video, gpx_path, output, framerate, b'gpmd')
    video = Path(video)
    if video.is_file():
        os.remove(video)
        
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

def write_metadata(mp4, gpx, output, framerate, metadata):
    #framerate = 1
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
                metadata_utils.inject_metadata(output_video, output, metadata,
                                                console)
                os.remove(output_video)
