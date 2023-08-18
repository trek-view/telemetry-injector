import collections
import os, sys, datetime, time, math
import re, json
import struct
import traceback

import xml.etree
import xml.etree.ElementTree as ET

import gpxpy
import gpxpy.gpx

class CammMetadataCase0():
    angle_axis_1 = 0.0 # float
    angle_axis_2 = 0.0 # float
    angle_axis_3 = 0.0 # float

    def write(self):
        data = b'\x00\x00\x00\x00'
        data += struct.pack("<f", self.angle_axis_1)
        data += struct.pack("<f", self.angle_axis_2)
        data += struct.pack("<f", self.angle_axis_3)
        return data

    def read(self, data):
        header = struct.unpack("<H", data[0:2])[0]
        case = struct.unpack("<H", data[2:4])[0]
        self.angle_axis_1 = struct.unpack("<f", data[4:8])[0]
        self.angle_axis_2 = struct.unpack("<f", data[8:12])[0]
        self.angle_axis_3 = struct.unpack("<f", data[12:16])[0]
    
    def data(self):
        return [
            self.angle_axis_1,
            self.angle_axis_2,
            self.angle_axis_3
        ]

class CammMetadataCase1():
    pixel_exposure_time = 0 # int32
    rolling_shutter_skew_time = 0 # int32

    def write(self):
        data = b'\x00\x00\x01\x00'
        data += struct.pack("<i", self.pixel_exposure_time)
        data += struct.pack("<i", self.rolling_shutter_skew_time)
        return data

    def read(self, data):
        header = struct.unpack("<H", data[0:2])[0]
        case = struct.unpack("<H", data[2:4])[0]
        self.pixel_exposure_time = struct.unpack("<i", data[4:8])[0]
        self.rolling_shutter_skew_time = struct.unpack("<i", data[8:12])[0]
    
    def data(self):
        return {
            'pixel_exposure_time': self.pixel_exposure_time,
            'rolling_shutter_skew_time': self.rolling_shutter_skew_time,
        }

class CammMetadataCase2():
    gyro_1 = 0.0 # float
    gyro_2 = 0.0 # float
    gyro_3 = 0.0 # float

    def write(self):
        data = b'\x00\x00\x02\x00'
        data += struct.pack("<f", self.gyro_1)
        data += struct.pack("<f", self.gyro_2)
        data += struct.pack("<f", self.gyro_3)
        return data

    def read(self, data):
        header = struct.unpack("<H", data[0:2])[0]
        case = struct.unpack("<H", data[2:4])[0]
        self.gyro_1 = struct.unpack("<f", data[4:8])[0]
        self.gyro_2 = struct.unpack("<f", data[8:12])[0]
        self.gyro_3 = struct.unpack("<f", data[12:16])[0]
    
    def data(self):
        return [
            self.gyro_1,
            self.gyro_2,
            self.gyro_3
        ]

class CammMetadataCase3():
    acceleration_1 = 0.0 # float
    acceleration_2 = 0.0 # float
    acceleration_3 = 0.0 # float

    def write(self):
        data = b'\x00\x00\x03\x00'
        data += struct.pack("<f", self.acceleration_1)
        data += struct.pack("<f", self.acceleration_2)
        data += struct.pack("<f", self.acceleration_3)
        return data

    def read(self, data):
        header = struct.unpack("<H", data[0:2])[0]
        case = struct.unpack("<H", data[2:4])[0]
        self.acceleration_1 = struct.unpack("<f", data[4:8])[0]
        self.acceleration_2 = struct.unpack("<f", data[8:12])[0]
        self.acceleration_3 = struct.unpack("<f", data[12:16])[0]
    
    def data(self):
        return [
            self.acceleration_1,
            self.acceleration_2,
            self.acceleration_3
        ]

class CammMetadataCase4():
    position_1 = 0.0 # float
    position_2 = 0.0 # float
    position_3 = 0.0 # float

    def write(self):
        data = b'\x00\x00\x04\x00'
        data += struct.pack("<f", self.position_1)
        data += struct.pack("<f", self.position_2)
        data += struct.pack("<f", self.position_3)
        return data

    def read(self, data):
        header = struct.unpack("<H", data[0:2])[0]
        case = struct.unpack("<H", data[2:4])[0]
        self.position_1 = struct.unpack("<f", data[4:8])[0]
        self.position_2 = struct.unpack("<f", data[8:12])[0]
        self.position_3 = struct.unpack("<f", data[12:16])[0]
    
    def data(self):
        return [
            self.position_1,
            self.position_2,
            self.position_3
        ]

class CammMetadataCase5():
    latitude = 0.0 # float
    longitude = 0.0 # float
    altitude = 0.0 # float

    def write(self):
        data = b'\x00\x00\x05\x00'
        data += struct.pack("<d", self.latitude)
        data += struct.pack("<d", self.longitude)
        data += struct.pack("<d", self.altitude)
        return data

    def read(self, data):
        header = struct.unpack("<H", data[0:2])[0]
        case = struct.unpack("<H", data[2:4])[0]
        self.latitude = struct.unpack("<d", data[4:12])[0]
        self.longitude = struct.unpack("<d", data[12:20])[0]
        self.altitude = struct.unpack("<d", data[20:28])[0]
    
    def data(self):
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'altitude': self.altitude,
        }

class CammMetadataCase6():
    time_gps_epoch = 0.0 # double
    gps_fix_type = 3 # int
    latitude = 0.0 # double
    longitude = 0.0 # double
    altitude = 0.0 # double
    horizontal_accuracy = 0.0 # float
    vertical_accuracy = 0.0 # float
    velocity_east = 0.0 # float
    velocity_north = 0.0 # float
    velocity_up = 0.0 # float
    speed_accuracy = 0.0 # float

    def write(self):
        data = b'\x00\x00\x06\x00'
        data += struct.pack("<d", self.time_gps_epoch)
        data += struct.pack("<i", self.gps_fix_type)
        data += struct.pack("<d", self.latitude)
        data += struct.pack("<d", self.longitude)
        data += struct.pack("<f", self.altitude)
        data += struct.pack("<f", self.horizontal_accuracy)
        data += struct.pack("<f", self.vertical_accuracy)
        data += struct.pack("<f", self.velocity_east)
        data += struct.pack("<f", self.velocity_north)
        data += struct.pack("<f", self.velocity_up)
        data += struct.pack("<f", self.speed_accuracy)
        return data

    def read(self, data):
        header = struct.unpack("<H", data[0:2])[0]
        case = struct.unpack("<H", data[2:4])[0]
        self.time_gps_epoch = struct.unpack("<d", data[4:12])[0]
        self.gps_fix_type = struct.unpack("<i", data[12:16])[0]
        self.latitude = struct.unpack("<d", data[16:24])[0]
        self.longitude = struct.unpack("<d", data[24:32])[0]
        self.altitude = struct.unpack("<f", data[32:36])[0]
        self.horizontal_accuracy = struct.unpack("<f", data[36:40])[0]
        self.vertical_accuracy = struct.unpack("<f", data[40:44])[0]
        self.velocity_east = struct.unpack("<f", data[44:48])[0]
        self.velocity_north = struct.unpack("<f", data[48:52])[0]
        self.velocity_up = struct.unpack("<f", data[52:56])[0]
        self.speed_accuracy = struct.unpack("<f", data[56:60])[0]
    
    def data(self):
        time_gps_epoch = datetime.datetime.utcfromtimestamp(self.time_gps_epoch)
        return {
            'time_gps_epoch': time_gps_epoch.isoformat() + 'Z',
            'gps_fix_type': self.gps_fix_type,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'altitude': self.altitude,
            'horizontal_accuracy': self.horizontal_accuracy,
            'vertical_accuracy': self.vertical_accuracy,
            'velocity_east': self.velocity_east,
            'velocity_north': self.velocity_north,
            'velocity_up': self.velocity_up,
            'speed_accuracy': self.speed_accuracy,
        }

class CammMetadataCase7():
    magnetic_field_1 = 0.0 # float
    magnetic_field_2 = 0.0 # float
    magnetic_field_3 = 0.0 # float

    def write(self):
        data = b'\x00\x00\x07\x00'
        data += struct.pack("<f", self.magnetic_field_1)
        data += struct.pack("<f", self.magnetic_field_2)
        data += struct.pack("<f", self.magnetic_field_3)
        return data

    def read(self, data):
        header = struct.unpack("<H", data[0:2])[0]
        case = struct.unpack("<H", data[2:4])[0]
        self.magnetic_field_1 = struct.unpack("<f", data[4:8])[0]
        self.magnetic_field_2 = struct.unpack("<f", data[8:12])[0]
        self.magnetic_field_3 = struct.unpack("<f", data[12:16])[0]
    
    def data(self):
        return [
            self.magnetic_field_1,
            self.magnetic_field_2,
            self.magnetic_field_3
        ]

class CammMetadata():
    def __init__(self):
        pass
    def read(self, data):
        c_data = None
        if len(data) >= 16:
            header = struct.unpack("<H", data[0:2])[0]
            case = struct.unpack("<H", data[2:4])[0]
            if case == 0:
                c = CammMetadataCase0()
                c.read(data)
                c_data = c.data()
                c_data = {
                    'type': 0,
                    'data': c_data
                }
            elif case == 1:
                c = CammMetadataCase1()
                c.read(data)
                c_data = c.data()
                c_data = {
                    'type': 1,
                    'data': c_data
                }
            elif case == 2:
                c = CammMetadataCase2()
                c.read(data)
                c_data = c.data()
                c_data = {
                    'type': 2,
                    'data': c_data
                }
            elif case == 3:
                c = CammMetadataCase3()
                c.read(data)
                c_data = c.data()
                c_data = {
                    'type': 3,
                    'data': c_data
                }
            elif case == 4:
                c = CammMetadataCase4()
                c.read(data)
                c_data = c.data()
                c_data = {
                    'type': 4,
                    'data': c_data
                }
            elif case == 5:
                c = CammMetadataCase5()
                c.read(data)
                c_data = c.data()
                c_data = {
                    'type': 5,
                    'data': c_data
                }
            elif case == 6:
                c = CammMetadataCase6()
                c.read(data)
                c_data = c.data()
                c_data = {
                    'type': 6,
                    'data': c_data
                }
            elif case == 7:
                c = CammMetadataCase7()
                c.read(data)
                c_data = c.data()
                c_data = {
                    'type': 7,
                    'data': c_data
                }
            else:
                c_data = None
        return c_data
    

def get_gpx_data(gpx_file):
    with open(gpx_file, "r") as f:
        g = gpxpy.parse(f)
        metadatas = []
        point_time = None
        data = {'metadata':[], 'duration': 0.0}
        first_time = datetime.datetime.now()
        for track in g.tracks:
            for segment in track.segments:
                for point in segment.points:
                    metadata = CammMetadataCase6()
                    metadata.time_gps_epoch = point.time.timestamp()
                    metadata.gps_fix_type = 3
                    metadata.latitude = point.latitude
                    metadata.longitude = point.longitude
                    metadata.altitude = point.elevation
                    if len(point.extensions) > 4:
                        metadata.horizontal_accuracy = float(point.extensions[0].text)
                        metadata.vertical_accuracy = float(point.extensions[1].text)
                        metadata.velocity_east = float(point.extensions[2].text)
                        metadata.velocity_north = float(point.extensions[3].text)
                        metadata.velocity_up = float(point.extensions[4].text)
                        metadata.speed_accuracy = float(point.extensions[5].text)
                    else:
                        metadata.horizontal_accuracy = 1.0
                        metadata.vertical_accuracy = 1.0
                        metadata.velocity_east = 0.5
                        metadata.velocity_north = 0.5
                        metadata.velocity_up = 0
                        metadata.speed_accuracy = 0
                    if point_time is None:
                        point_time = point.time
                        first_time = point.time
                    metadata_time = "{0:.06}".format(point.time.timestamp() - point_time.timestamp())
                    metadatas.append({
                        'metadata': metadata.write(),
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
