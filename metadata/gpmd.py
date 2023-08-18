import collections
import os, sys, datetime, time, math
import re, json
import struct
import traceback

import xml.etree
import xml.etree.ElementTree as ET

import gpxpy
import gpxpy.gpx

from .gpmd_klvs import pack_klv

def since1904(seconds):
    return datetime.datetime(1904, 1, 1, 0, 0, 0, 0) + datetime.timedelta(seconds=seconds)

def getTimeBySeconds(seconds):
    return datetime.datetime.strftime(since1904(seconds), "%H:%M:%S")

class Gpmf(object):
    
    def __init__(self):
        self.key = ""
        self.type = 0
        self.size = 0
        self.repeat = 0
        self.childrens = []
        self.data = b''
    
    def get_binary_value(self, FourCC, ktype, size, repeat, values, scal_value):
        data = FourCC+chr(ktype).encode('utf-8')
        data += struct.pack(">b", size)
        data += struct.pack(">H", repeat)
        data += pack_klv(values, FourCC, ktype, size, repeat, scal_value)
        return data
    def get_gps_binary(self):
        data = b''
        ignore_keys = [
            b'AALP', b'MWET', b'WNDM', b'DISP', 
            b'GRAV', b'IORI', b'CORI', b'UNIF', 
            b'WBAL', b'ISOE', b'WRGB', b'SHUT',
            b'MAGN', b'GYRO', b'ACCL'
        ]
        scal = None
        for i in self.childrens:
            if i.type == 0:
                child_data = b''
                kkeys = []
                for ii in i.childrens:
                    kkeys.append(ii.key)
                fount_igone_key = False
                for ik in ignore_keys:
                    if ik in kkeys:
                        fount_igone_key = True
                if fount_igone_key:
                    continue
                
                for j in i.childrens:
                    values = []

                    if j.key == b'TSMP':
                        j.childrens[0]['data'] = [[1]]
                    if j.key == b'GPS5':
                        j.repeat = 1
                        j.childrens[0]['data'] = [j.childrens[0]['data'][0]]

                    if j.key == b'SCAL':
                        scal = j.childrens[0]['data']
                    
                    if j.type != 0 and len(j.childrens) > 0:
                        if 'data' in j.childrens[0]:
                            values = j.childrens[0]['data']

                            klv_data = self.get_binary_value(j.key, j.type, j.size, j.repeat, values, scal)
                            
                            if klv_data != b'':
                                child_data += klv_data
                
                Length = len(child_data)
                if Length%4 != 0:
                    new_length = Length + (4 - Length%4)
                    for l in range(0, (new_length - Length)):
                        child_data += b'\x00'
                Length = len(child_data)
                klv_container_data = i.key
                klv_container_data += struct.pack(">b", 0)
                klv_container_data += struct.pack(">b", 1)
                klv_container_data += struct.pack(">H", Length)
                klv_container_data += child_data
                child_data = klv_container_data    
                data += child_data
            else:
                if len(i.childrens) > 0:
                    if 'data' in i.childrens[0]:
                        values = i.childrens[0]['data']
                        klv_data = self.get_binary_value(i.key, i.type, i.size, i.repeat, values, scal)
                        if klv_data != b'':
                            data += klv_data
        klv_data = b'DEVC'
        klv_data += struct.pack(">b", 0)
        klv_data += struct.pack(">b", 1)
        klv_data += struct.pack(">H", len(data))
        klv_data += data
        return klv_data
        
    def read_klv(self, data, start, end):
        FourCC, Type, Size, Repeat, err = '', 0, 0, 0, True
        if len(data[start:end]) >= 8:
            start = start
            end = start+4
            FourCC = data[start:end]
            start = end
            end = start+1
            Type = struct.unpack(">b", data[start:end])[0]
            start = end
            end = start+1
            Size = struct.unpack(">b", data[start:end])[0]
            start = end
            end = start+2
            Repeat = struct.unpack(">H", data[start:end])[0]
            err = False
        return FourCC, Type, Size, Repeat, err

def get_gpx_data(gpx_file):
    with open(gpx_file, "r") as f:
        g = gpxpy.parse(f)
        metadatas = []
        point_time = None
        data = {'metadata':[], 'duration': 0.0}
        first_time = datetime.datetime.now()
        metadatas = []
        point_time = None
        data = {'metadata':[], 'duration': 0.0}
        for track in g.tracks:
            for segment in track.segments:
                for point in segment.points:
                    timestamp = datetime.datetime.fromtimestamp(point.time.timestamp()).strftime('%Y-%m-%dT%H:%M:%S.%f')
                    devc_size = 0
                    gpmf = Gpmf()
                    gpmf.key = b'DEVC'
                    gpmf.type = 0
                    gpmf.size = 0
                    gpmf.repeat = 1

                    dvid = Gpmf()
                    dvid.key = b'DVID'
                    dvid.type = ord('L')
                    dvid.size = 4
                    dvid.repeat = 1
                    dvid.childrens.append({
                        'data': 1.0
                    })
                    
                    device = b'Trek View Telemetry Injector'
                    dvnm = Gpmf()
                    dvnm.key = b'DVNM'
                    dvnm.type = ord('c')
                    dvnm.size = 1
                    dvnm.repeat = len(device)
                    dvnm.childrens.append({
                        'data': device
                    })
                    
                    strm = Gpmf()
                    strm.key = b'STRM'
                    strm.type = 0
                    strm.size = 0
                    strm.repeat = 1
                    gpmf.childrens.append(dvid)
                    gpmf.childrens.append(dvnm)
                    
                    stmp = Gpmf()
                    stmp.key = b'STMP'
                    stmp.type = ord('J')
                    stmp.size = 8
                    stmp.repeat = 1
                    stmp.childrens.append({
                        'data': 1001
                    })
                    strm.childrens.append(stmp)
                    
                    tsmp = Gpmf()
                    tsmp.key = b'TSMP'
                    tsmp.type = ord('L')
                    tsmp.size = 4
                    tsmp.repeat = 1
                    tsmp.childrens.append({
                        'data': 1
                    })
                    strm.childrens.append(tsmp)
                    
                    stnm = Gpmf()
                    stnm.key = b'STNM'
                    stnm.type = ord('c')
                    stnm.size = 43
                    stnm.repeat = 1
                    stnm.childrens.append({
                        'data': b'GPS (Lat., Long., Alt., 2D speed, 3D speed)'
                    })
                    strm.childrens.append(stnm)
                    
                    gpsf = Gpmf()
                    gpsf.key = b'GPSF'
                    gpsf.type = ord('L')
                    gpsf.size = 4
                    gpsf.repeat = 1
                    gpsf.childrens.append({
                        'data': 3
                    })
                    strm.childrens.append(gpsf)
                    gpsu_timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f')
                    gpsu_timestamp = datetime.datetime.strftime(gpsu_timestamp, '%y%m%d%H%M%S.%f')
                    
                    gpsu = Gpmf()
                    gpsu.key = b'GPSU'
                    gpsu.type = ord('U')
                    gpsu.size = len(gpsu_timestamp[0:16])
                    gpsu.repeat = 1
                    gpsu.childrens.append({
                        'data': gpsu_timestamp[0:16]
                    })
                    strm.childrens.append(gpsu)
                    
                    gpsp = Gpmf()
                    gpsp.key = b'GPSP'
                    gpsp.type = ord('S')
                    gpsp.size = 2
                    gpsp.repeat = 1
                    gpsp.childrens.append({
                        'data': [[537]]
                    })
                    strm.childrens.append(gpsp)
                    
                    unit = Gpmf()
                    unit.key = b'UNIT'
                    unit.type = ord('c')
                    unit.size = 3
                    unit.repeat = 5
                    unit.childrens.append({
                        'data': b'degdegm\x00\x00m/sm/s\x00'
                    })
                    strm.childrens.append(unit)
                    
                    scal = Gpmf()
                    scal.key = b'SCAL'
                    scal.type = ord('l')
                    scal.size = 4
                    scal.repeat = 5
                    lat_scale = 10000000.0
                    lng_scale = 10000000.0
                    alt_scale = 1000.0
                    speed_scale = 1000.0
                    speed_3d_scale = 100.0
                    scal.childrens.append({
                        'data': [[lat_scale, lng_scale, alt_scale, speed_scale, speed_scale]]
                    })
                    strm.childrens.append(scal)
                    
                    gpsa = Gpmf()
                    gpsa.key = b'GPSA'
                    gpsa.type = ord('F')
                    gpsa.size = 4
                    gpsa.repeat = 1
                    gpsa.childrens.append({
                        'data': [[b'MSLV']]
                    })
                    strm.childrens.append(gpsa)
                    
                    gps5 = Gpmf()
                    gps5.key = b'GPS5'
                    gps5.type = ord('l')
                    gps5.size = 20
                    gps5.repeat = 1
                    gps5.childrens.append({
                        'data': [[
                            point.latitude,
                            point.longitude,
                            point.elevation,
                            0.865,
                            0.89,
                        ]]
                    })
                    
                    strm.childrens.append(gps5)
                    
                    gpmf.childrens.append(strm)
                    
                    d = gpmf.get_gps_binary()
                    
                    if point_time is None:
                        point_time = point.time
                        first_time = point.time
                    
                    metadata_time = "{0:.06}".format(point.time.timestamp() - point_time.timestamp())
                    metadatas.append({
                        'metadata': d,
                        'time': metadata_time
                    })
                    
                    point_time = point.time
                    
                    
        total_seconds = 0.0
        if point_time is not None:
            total_seconds = (point_time - first_time).total_seconds()
        data['metadata'] = metadatas
        data['duration'] = total_seconds
        data['start_time'] = first_time
        return data
