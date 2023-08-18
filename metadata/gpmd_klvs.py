import collections
import os, sys, datetime, time, math
import re, json
import struct
import traceback

import xml.etree
import xml.etree.ElementTree as ET

import gpxpy
import gpxpy.gpx

def get_klv_size(ktype):
    size = 4
    btype = '>I'
    if chr(ktype) == 'b':
        size = 1
        btype = '>b'
    elif chr(ktype) == 'c':
        size = 1
        btype = '>c'
    elif chr(ktype) == 'B':
        size = 1
        btype = '>b'
    elif chr(ktype) == 'l':
        size = 4
        btype = '>i'
    elif chr(ktype) == 'L':
        size = 4
        btype = '>L'
    elif chr(ktype) == 'q':
        size = 4
        btype = '>f'
    elif chr(ktype) == 'Q':
        size = 8
        btype = '>Q'
    elif chr(ktype) == 'd':
        size = 8
    elif chr(ktype) == 'j':
        size = 8
        btype = '>Q'
    elif chr(ktype) == 'J':
        size = 8
        btype = '>Q'
    elif chr(ktype) == 'f':
        size = 4
        btype = '>f'
    elif chr(ktype) == 'F':
        size = 1
        btype = '>s'
    elif chr(ktype) == 's':
        size = 2
        btype = '>h'
    elif chr(ktype) == 'S':
        size = 2
        btype = '>H'
    elif chr(ktype) == 'U':
        size = 2
        btype = '>U'
    else:
        btype = None
    return size, btype

def get_pack_data(data, ktype):
    klv_data = b''
    if (chr(ktype) == 'l'):
        data = int(data)
        klv_data = struct.pack('>i', data)
    if (chr(ktype) == 'L'):
        data = int(data)
        klv_data = struct.pack('>I', data)
    elif (chr(ktype) == 's'):
        data = int(data)
        klv_data = struct.pack('>h', data)
    elif (chr(ktype) == 'S'):
        data = int(data)
        klv_data = struct.pack('>H', data)
    elif (chr(ktype) == 'F'):
        klv_data = data[0:4]
    elif (chr(ktype) == 'c'):
        if type(data) == str:
            data = data.encode('utf-8')
        data = pad_klv_bytes(data)
        klv_data = data
    elif (chr(ktype) == 'U'):
        gpsu = data.encode('utf-8')
        klv_data = pad_klv_bytes(gpsu)
    return klv_data

def pack_klv(data, FourCC, ktype, size, repeat, scal_value):
    klv_size, btype = get_klv_size(ktype)
    klv_count = math.ceil(size/klv_size)
    klv_data = []
    index = 0
    scal = None
    scal_four_cc = [b'GYRO', b'ACCL', b'GPS5', b'CORI', b'IORI', b'MAGN', b'GRAV']
    if scal_value:
        scal = scal_value[0]
        if type(scal) == list:
            if len(scal) == 1:
                scal = scal[0]
    klv_data = b''
    if type(data) == list:
        for k in data:
            j = 0
            for v in k:
                if scal and (FourCC in scal_four_cc) :
                    if type(scal) == list:
                        v = v*scal[j]
                    else:
                        v = v*scal
                j += 1
                k_data = get_pack_data(v, ktype)
                if k_data == b'':
                    k_data = struct.pack(btype, v)
                if (chr(ktype) == 's' or chr(ktype) == 'S') and (FourCC not in scal_four_cc):
                    k_data = pad_klv_bytes(k_data)
                klv_data += k_data 
    else:
        if btype == None:
            klv_data = data
        else:
            klv_data = get_pack_data(data, ktype)
            if klv_data == b'':
                klv_data = struct.pack(btype, data)
    return klv_data

def pad_klv_bytes(data):
    if data != b'':
        Length = len(data)
        if Length%4 != 0:
            new_length = Length + (4 - Length%4)
            for i in range(0, (new_length - Length)):
                data += b'\x00'
    return data
