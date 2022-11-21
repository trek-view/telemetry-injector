import collections
import os, sys, datetime, time, math
import re
import struct
import traceback
import xml.etree
import xml.etree.ElementTree

from decimal import *

from spatialmedia import mpeg

from spatialmedia import mpeg as mpeg4_container

import struct

#import box
#import constants
from spatialmedia.mpeg import box
from spatialmedia.mpeg import constants
from spatialmedia.mpeg import container

import gpxpy
import gpxpy.gpx
from calendar import timegm

from .camm import *
from .gpmd import *

def since1904_to_seconds(dt):
    start = datetime.datetime.strptime('1904-1-1T00:00:00.000', '%Y-%m-%dT%H:%M:%S.%f')
    end = datetime.datetime.strptime(
        datetime.datetime.strftime(dt, '%Y-%m-%dT%H:%M:%S.%f'), '%Y-%m-%dT%H:%M:%S.%f')
    return (end - start).total_seconds()

def since1904(seconds):
    return datetime.datetime(1904, 1, 1, 0, 0, 0, 0) + datetime.timedelta(seconds=seconds)

def getTimeBySeconds(seconds):
    return datetime.datetime.strftime(since1904(seconds), "%H:%M:%S")

class TrakBox(box.Box):

    def __init__(self):
        box.Box.__init__(self)
        self.name = constants.TAG_TRAK
        self.header_size = 8
        self.version = 0

    @staticmethod
    def create():
        new_box = SA3DBox()
        new_box.header_size = 8
        new_box.name = constants.TAG_TRAK
        new_box.version = 0                     # uint8
        new_box.content_size += 1               # uint8
        return new_box

    def print_box(self, console):
        pass

    def get_metadata_string(self):
        return ""
        pass

    def save(self, in_fh, out_fh, delta):
        pass

class StsdBox(box.Box):

    def __init__(self):
        box.Box.__init__(self)
        self.name = b'stsd'
        self.header_size = 8
        self.version = 0
        self.entries = []
        self.data_format = b''
        self.format_data = None
        self.data_size = 16
        self.entries = []

    def load(self, in_fh, position):
        if position is None:
            position = in_fh.tell()

        in_fh.seek(position)
        header = in_fh.read(self.header_size)
        header_size = struct.unpack(">I", header[0:4])[0]
        header_name = header[4:8]
        if header_name == self.name and header_size > self.header_size:
            version_flags = in_fh.read(4)
            number_of_entries = in_fh.read(4)
            number_of_entries = struct.unpack(">L", number_of_entries)[0]
            #print('header_size', header_size)
            #print('number_of_entries', number_of_entries)
            for i in range(0, number_of_entries):
                data_size = in_fh.read(4)
                self.data_size = struct.unpack(">L", data_size)[0]
                data_format = in_fh.read(4)
                self.data_format = data_format
                self.format_data = in_fh.read(self.data_size-8)
                self.entries.append([self.data_format, self.format_data])
                #print(self.data_size, self.data_format, self.format_data)
    def getValues(self):
        return {
            'entries': self.entries,
            'values': len(self.entries),
        }
    
    @staticmethod
    def create():
        new_box = StsdBox()
        new_box.header_size = 8
        new_box.name = b'stsd'
        new_box.version = 0                     # uint8
        new_box.content_size += 4               # uint8

        new_box.content_size += 4
        
        new_box.content_size += 4

        new_box.content_size += 4

        new_box.content_size += 4

        new_box.content_size += 4

        return new_box

    def print_box(self, console):
        pass

    def get_metadata_string(self):
        return ""
        pass

    def save(self, in_fh, out_fh, delta):
        if (self.header_size == 16):
            out_fh.write(struct.pack(">I", 1))
            out_fh.write(struct.pack(">Q", self.size()))
            out_fh.write(self.name)
        elif(self.header_size == 8):
            out_fh.write(struct.pack(">I", self.size()))
            out_fh.write(self.name)
        out_fh.write(struct.pack(">I", 0)) # version flags
        out_fh.write(struct.pack(">L", 1)) # number of entries
        out_fh.write(struct.pack(">L", self.data_size)) # number of entries
        #print('!!!!', self.data_format, self.data_size, self.format_data)
        out_fh.write(self.data_format)
        if self.format_data:
            out_fh.write(self.format_data)
        else:
            out_fh.write(struct.pack(">I", 0)) 
            out_fh.write(struct.pack(">I", 1)) 

class SttsBox(box.Box):

    def __init__(self):
        box.Box.__init__(self)
        self.name = constants.TAG_STTS
        self.header_size = 8
        self.version = 0
        self.entries = 0
        self.times = []

    def getValues(self):
        return {
            'entries': self.entries,
            'values': self.times,
        }

    def load(self, in_fh, position):
        if position is None:
            position = in_fh.tell()

        in_fh.seek(position)
        header = in_fh.read(self.header_size)
        header_size = struct.unpack(">I", header[0:4])[0]
        header_name = header[4:8]

        if header_name == self.name and header_size > self.header_size:
            version_flags = in_fh.read(4)
            number_of_entries = in_fh.read(4)
            number_of_entries = struct.unpack(">L", number_of_entries)[0]
            self.entries = number_of_entries
            for i in range(0, number_of_entries):
                frame_count = in_fh.read(4)
                frame_count = struct.unpack(">L", frame_count)[0]
                frame_duration = in_fh.read(4)
                frame_duration = struct.unpack(">L", frame_duration)[0]

                self.times.append([frame_count, frame_duration])




    @staticmethod
    def create(times):
        new_box = SttsBox()
        new_box.header_size = 8
        new_box.name = constants.TAG_STTS
        new_box.version = 0                     # uint8
        new_box.content_size += 4               # uint8

        new_box.content_size += 4

        for i in times:
            new_box.content_size += 4
            new_box.content_size += 4

        return new_box

    def print_box(self, console):
        pass

    def get_metadata_string(self):
        return ""
        pass

    def save(self, in_fh, out_fh, delta):
        if (self.header_size == 16):
            out_fh.write(struct.pack(">I", 1))
            out_fh.write(struct.pack(">Q", self.size()))
            out_fh.write(self.name)
        elif(self.header_size == 8):
            out_fh.write(struct.pack(">I", self.size()))
            out_fh.write(self.name)
        out_fh.write(struct.pack(">L", 0)) # version flags
        out_fh.write(struct.pack(">L", len(self.times))) # number of entries
        for i in self.times:
            out_fh.write(struct.pack(">L", i[0]))
            out_fh.write(struct.pack(">L", i[1]))

class StscBox(box.Box):

    def __init__(self):
        box.Box.__init__(self)
        self.name = constants.TAG_STSC
        self.header_size = 8
        self.version = 0
        self.frames = []

    def getValues(self):
        return {
            'values': self.frames,
        }

    def load(self, in_fh, position):
        if position is None:
            position = in_fh.tell()

        in_fh.seek(position)
        header = in_fh.read(self.header_size)
        header_size = struct.unpack(">I", header[0:4])[0]
        header_name = header[4:8]
        if header_name == self.name and header_size > self.header_size:

            version_flags = in_fh.read(4)
            number_of_blocks = in_fh.read(4)
            number_of_blocks = struct.unpack(">L", number_of_blocks)[0]
            
            for i in range(0, number_of_blocks):
                first_next_block = in_fh.read(4)
                first_next_block = struct.unpack(">L", first_next_block)[0]
                numbers_of_frames = in_fh.read(4)
                numbers_of_frames = struct.unpack(">L", numbers_of_frames)[0]
                description_id = in_fh.read(4)
                description_id = struct.unpack(">L", description_id)[0]
                self.frames.append([first_next_block, numbers_of_frames, description_id])
    @staticmethod
    def create(frames):
        new_box = StscBox()
        new_box.header_size = 8
        new_box.name = constants.TAG_STSC
        new_box.version = 0                     # uint8
        new_box.content_size += 4               # uint8

        new_box.content_size += 4

        for i in frames:
            new_box.content_size += 4
            new_box.content_size += 4
            new_box.content_size += 4

        return new_box

    def print_box(self, console):
        pass

    def get_metadata_string(self):
        return ""
        pass

    def save(self, in_fh, out_fh, delta):
        if (self.header_size == 16):
            out_fh.write(struct.pack(">I", 1))
            out_fh.write(struct.pack(">Q", self.size()))
            out_fh.write(self.name)
        elif(self.header_size == 8):
            out_fh.write(struct.pack(">I", self.size()))
            out_fh.write(self.name)
        out_fh.write(struct.pack(">I", 0)) # version flags
        out_fh.write(struct.pack(">L", len(self.frames))) # number of entries
        for i in self.frames:
            out_fh.write(struct.pack(">L", i[0]))
            out_fh.write(struct.pack(">L", i[1]))
            out_fh.write(struct.pack(">L", i[2]))

class StszBox(box.Box):

    def __init__(self):
        box.Box.__init__(self)
        self.name = constants.TAG_STSZ
        self.header_size = 8
        self.version = 0
        self.entries = 0
        self.sizes = []
        self.block_size = 0

    def getValues(self):
        return {
            'size': self.block_size,
            'entries': self.entries,
            'values': self.sizes,
        }

    def load(self, in_fh, position):
        if position is None:
            position = in_fh.tell()

        in_fh.seek(position)
        header = in_fh.read(self.header_size)
        header_size = struct.unpack(">I", header[0:4])[0]
        header_name = header[4:8]
        if header_name == self.name and header_size > self.header_size:
            version_flags = in_fh.read(4)
            block_size = in_fh.read(4)
            self.block_size = struct.unpack(">L", block_size)[0]

            number_of_blocks = in_fh.read(4)
            number_of_blocks = struct.unpack(">L", number_of_blocks)[0]
            self.entries = number_of_blocks
            
            for i in range(0, number_of_blocks):
                sample_size = in_fh.read(4)
                sample_size = struct.unpack(">L", sample_size)[0]
                self.sizes.append(sample_size)

    @staticmethod
    def create(sizes):
        new_box = StszBox()
        new_box.header_size = 8
        new_box.name = constants.TAG_STSZ
        new_box.version = 0                     # uint8
        new_box.content_size += 4               # uint8
        new_box.content_size += 4
        new_box.content_size += 4

        for i in sizes:
            new_box.content_size += 4

        return new_box

    def print_box(self, console):
        pass

    def get_metadata_string(self):
        return ""
        pass

    def save(self, in_fh, out_fh, delta):
        if (self.header_size == 16):
            out_fh.write(struct.pack(">I", 1))
            out_fh.write(struct.pack(">Q", self.size()))
            out_fh.write(self.name)
        elif(self.header_size == 8):
            out_fh.write(struct.pack(">I", self.size()))
            out_fh.write(self.name)
        out_fh.write(struct.pack(">I", 0)) # version flags
        out_fh.write(struct.pack(">L", 0)) # number of entries
        out_fh.write(struct.pack(">L", len(self.sizes))) # number of entries

        for i in self.sizes:
            out_fh.write(struct.pack(">L", i))

class StcoBox(box.Box):

    def __init__(self):
        box.Box.__init__(self)
        self.name = b"stco"
        self.header_size = 8
        self.version = 0
        self.entries = 0
        self.number_of_offsets = 0
        self.offsets = []

    def getValues(self):
        return {
            'entries': self.entries,
            'values': self.offsets,
        }

    def load(self, in_fh, position):
        if position is None:
            position = in_fh.tell()
        
        in_fh.seek(position)
        header = in_fh.read(self.header_size)
        header_size = struct.unpack(">I", header[0:4])[0]
        header_name = header[4:8]
        if header_name == self.name and header_size > self.header_size:
            version_flags = in_fh.read(4)
            number_of_offsets = in_fh.read(4)
            number_of_offsets = struct.unpack(">L", number_of_offsets)[0]
            self.entries = number_of_offsets
            for i in range(0, number_of_offsets):
                offset = in_fh.read(4)
                offset = struct.unpack(">L", offset)[0]
                self.offsets.append(offset)

    @staticmethod
    def create(offsets):
        new_box = StcoBox()
        new_box.header_size = 8
        new_box.name = b'stco'
        new_box.version = 0                     # uint8
        new_box.content_size += 4               # uint8

        new_box.content_size += 4

        for i in offsets:
            new_box.content_size += 4
        return new_box

    def print_box(self, console):
        pass

    def get_metadata_string(self):
        return ""
        pass

    def save(self, in_fh, out_fh, delta):
        if (self.header_size == 16):
            out_fh.write(struct.pack(">I", 1))
            out_fh.write(struct.pack(">Q", self.size()))
            out_fh.write(self.name)
        elif(self.header_size == 8):
            out_fh.write(struct.pack(">I", self.size()))
            out_fh.write(self.name)
        out_fh.write(struct.pack(">I", 0)) # version flags
        out_fh.write(struct.pack(">L", len(self.offsets))) # number of entries
        for i in self.offsets:
            out_fh.write(struct.pack(">L", i))

class Co64Box(box.Box):

    def __init__(self):
        box.Box.__init__(self)
        self.name = constants.TAG_CO64
        self.header_size = 8
        self.version = 0
        self.entries = 0
        self.number_of_offsets = 0
        self.offsets = []

    def getValues(self):
        return {
            'entries': self.entries,
            'values': self.offsets,
        }

    def load(self, in_fh, position):
        if position is None:
            position = in_fh.tell()
        
        in_fh.seek(position)
        header = in_fh.read(self.header_size)
        header_size = struct.unpack(">I", header[0:4])[0]
        header_name = header[4:8]
        if header_name == self.name and header_size > self.header_size:
            version_flags = in_fh.read(4)
            number_of_offsets = in_fh.read(4)
            number_of_offsets = struct.unpack(">L", number_of_offsets)[0]
            self.entries = number_of_offsets
            for i in range(0, number_of_offsets):
                offset = in_fh.read(8)
                offset = struct.unpack(">Q", offset)[0]
                self.offsets.append(offset)

    @staticmethod
    def create(offsets):
        new_box = Co64Box()
        new_box.header_size = 8
        new_box.name = constants.TAG_CO64
        new_box.version = 0                     # uint8
        new_box.content_size += 4               # uint8

        new_box.content_size += 4

        for i in offsets:
            new_box.content_size += 8
        return new_box

    def print_box(self, console):
        pass

    def get_metadata_string(self):
        return ""
        pass

    def save(self, in_fh, out_fh, delta):
        if (self.header_size == 16):
            out_fh.write(struct.pack(">I", 1))
            out_fh.write(struct.pack(">Q", self.size()))
            out_fh.write(self.name)
        elif(self.header_size == 8):
            out_fh.write(struct.pack(">I", self.size()))
            out_fh.write(self.name)
        out_fh.write(struct.pack(">I", 0)) # version flags
        out_fh.write(struct.pack(">L", len(self.offsets))) # number of entries
        for i in self.offsets:
            out_fh.write(struct.pack(">Q", i))

class CammBox(box.Box):

    def __init__(self):
        box.Box.__init__(self)
        self.name = constants.TAG_CAMM
        self.header_size = 8
        self.version = 0
        self.reserved = 0
        self.packet_type = 1

    def load(self, in_fh, position):
        if position is None:
            position = in_fh.tell()

        total_bytes_read = 0

        in_fh.seek(position)
        header = in_fh.read(self.header_size)
        header_size = struct.unpack(">I", header[0:4])[0]
        header_name = header[4:8]
        if header_name == self.name:
            reserved = in_fh.read(4)
            reserved = struct.unpack(">I", reserved)[0]
            packet_type = in_fh.read(4)
            packet_type = struct.unpack(">I", packet_type)[0]

    @staticmethod
    def create():
        new_box = CammBox()
        new_box.header_size = 8
        new_box.name = constants.TAG_CAMM

        new_box.reserved = 0
        new_box.content_size += 4
        new_box.packet_type = 1
        new_box.content_size += 4

        return new_box

    def print_box(self, console):
        pass

    def get_metadata_string(self):
        return ""
        pass

    def save(self, in_fh, out_fh, delta):
        if (self.header_size == 16):
            out_fh.write(struct.pack(">I", 1))
            out_fh.write(struct.pack(">Q", self.size()))
            out_fh.write(self.name)
        elif(self.header_size == 8):
            out_fh.write(struct.pack(">I", self.size()))
            out_fh.write(self.name) 
        out_fh.write(struct.pack("<I", self.reserved)) # reserved
        out_fh.write(struct.pack("<I", self.packet_type)) # case 1

class IlstBox(box.Box):

    def __init__(self):
        box.Box.__init__(self)
        self.name = b"ilst"
        self.header_size = 8
        self.version = 0
        self.position = None

    def load(self, in_fh, position):
        if position is None:
            position = in_fh.tell()

        total_bytes_read = 0

        in_fh.seek(position)
        header = in_fh.read(self.header_size)
        header_size = struct.unpack(">I", header[0:4])[0]
        header_name = header[4:8]
        if header_name == self.name:
            header = in_fh.read(self.header_size)
            for i in range(0, 10):
                position = in_fh.tell()
                b = in_fh.read(self.header_size)
                if b != b'':
                    b_size = struct.unpack(">I", b[0:4])[0]
                    b_name = b[4:8]
                    if b_name == b"data":
                        b = in_fh.read(b_size-8)
                    in_fh.seek(position+b_size)


    @staticmethod
    def create():
        new_box = IlstBox()
        new_box.header_size = 8
        new_box.name = b"ilst"
        new_box.version = 0                     # uint8
        new_box.content_size += 1               # uint8
        return new_box

    def print_box(self, console):
        pass

    def get_metadata_string(self):
        return ""
        pass

    def save(self, in_fh, out_fh, delta):
        pass

class HdlrBox(box.Box):

    def __init__(self):
        box.Box.__init__(self)
        self.name = constants.TAG_HDLR
        self.header_size = 8
        self.version = 0
        self.position = None

        self.component_type = 0
        self.component_sub_type = 0
        self.component_manufacturer = 0
        self.component_flags = 0
        self.component_flags_mask = 0
        self.component_name = ''

        self.quicktime_type = 0
        self.subtype_metadata_type = 0
        self.quicktime_manufacutured_reserved = 0
        self.quicktime_component_reserved_flags = 0
        self.quicktime_component_reserved_flags_mask = 0
        self.quicktime_component_reserved_flags_mask = 0
        self.component_name_string_end = 0

    def load(self, in_fh, position):
        if position is None:
            position = in_fh.tell()
        pp = in_fh.tell()
        total_bytes_read = 0

        in_fh.seek(position)
        header = in_fh.read(self.header_size)
        header_size = struct.unpack(">I", header[0:4])[0]
        header_name = header[4:8]
        if header_name == self.name:
            version_flag = in_fh.read(4)

            self.component_type = in_fh.read(4)
            self.component_sub_type = in_fh.read(4)
            self.component_manufacturer = struct.unpack(">I", in_fh.read(4))[0]
            self.component_flags = struct.unpack(">I", in_fh.read(4))[0]
            self.component_flags_mask = struct.unpack(">I", in_fh.read(4))[0]
            component_length = header_size - 8 - (6*4)
            self.component_name = in_fh.read(component_length)

            self.quicktime_type = in_fh.read(4)
            self.subtype_metadata_type = in_fh.read(4)
            self.quicktime_manufacutured_reserved = in_fh.read(4)
            self.quicktime_component_reserved_flags = in_fh.read(4)
            self.quicktime_component_reserved_flags_mask = in_fh.read(4)
            self.quicktime_component_reserved_flags_mask = in_fh.read(4)
            self.component_name_string_end = in_fh.read(1)
            
            
            

    def getValues(self):
        return {
            "component_type": str(self.component_type, 'utf-8'),
            "component_sub_type": str(self.component_sub_type, 'utf-8'),
            "component_manufacturer": self.component_manufacturer,
            "component_flags": self.component_flags,
            "component_flags_mask": self.component_flags_mask,
            "component_name": str(self.component_name, 'utf-8'),
        }

    @staticmethod
    def create():
        new_box = HdlrBox()
        new_box.header_size = 8
        new_box.name = constants.TAG_HDLR
        new_box.version = 0                     # uint8
        new_box.content_size += 4               # uint8

        new_box.quicktime_type = b''
        new_box.content_size += 0
        new_box.subtype_metadata_type = b''
        new_box.content_size += 0
        new_box.quicktime_manufacutured_reserved = b'\x00\x00\x00\x00'
        new_box.content_size += 4
        new_box.quicktime_component_reserved_flags = b'\x00\x00\x00\x00'
        new_box.content_size += 4
        new_box.quicktime_component_reserved_flags_mask = b''
        new_box.content_size += 0
        new_box.component_name_string_end = b'\x00'
        new_box.content_size += 1

        return new_box

    def print_box(self, console):
        pass

    def get_metadata_string(self):
        return ""
        pass

    def save(self, in_fh, out_fh, delta):
        if (self.header_size == 16):
            out_fh.write(struct.pack(">I", 1))
            out_fh.write(struct.pack(">Q", self.size()))
            out_fh.write(self.name)
        elif(self.header_size == 8):
            out_fh.write(struct.pack(">I", self.size()))
            out_fh.write(self.name)

        data = b''
        data += struct.pack(">I", 0)
        data += self.quicktime_type
        data += self.subtype_metadata_type
        data += self.quicktime_manufacutured_reserved
        data += self.quicktime_component_reserved_flags
        data += self.quicktime_component_reserved_flags_mask
        data += self.component_name_string_end
        
        out_fh.write(data)
        #print('++', data)

        """out_fh.write() # version flags
        out_fh.write() # quicktime type
        out_fh.write() # subtype metadata type
        out_fh.write() # quicktime manufacutured reserved
        out_fh.write() # quicktime component reserved flags
        out_fh.write() # quicktime component reserved flags mask
        out_fh.write() # component name string end"""

class MdhdBox(box.Box):

    def __init__(self):
        box.Box.__init__(self)
        self.name = constants.TAG_MDHD
        self.header_size = 8
        self.version = 0
        self.creation_time = 0
        self.modification_time = 0
        self.time_scale = 0
        self.duration = 0
        self.language = 0
        self.quality = 0

    def load(self, in_fh, position):
        if position is None:
            position = in_fh.tell()

        total_bytes_read = 0

        in_fh.seek(position)
        header = in_fh.read(self.header_size)
        header_size = struct.unpack(">I", header[0:4])[0]
        
        header_name = header[4:8]
        if header_name == self.name:
            version_flag = in_fh.read(4)
            self.creation_time = struct.unpack(">I", in_fh.read(4))[0]
            #self.creation_time = since1904(self.creation_time)
            self.modification_time = struct.unpack(">I", in_fh.read(4))[0]
            #self.modification_time = since1904(self.modification_time)
            self.time_scale = struct.unpack(">I", in_fh.read(4))[0]
            self.duration = struct.unpack(">I", in_fh.read(4))[0]
            self.language = struct.unpack(">H", in_fh.read(2))[0]
            self.quality = struct.unpack(">H", in_fh.read(2))[0]

    def getValues(self):
        return {
            'creation_time': self.creation_time,
            'modification_time': self.modification_time,
            'time_scale': self.time_scale,
            'duration': self.duration,
            'language': self.language,
            'quality': self.quality,
        }

    @staticmethod
    def create():
        new_box = MdhdBox()
        new_box.header_size = 8
        new_box.name = constants.TAG_MDHD
        new_box.version = 0                     # uint8
        new_box.content_size += 4               # uint8

        new_box.creation_time = 0
        new_box.content_size += 4
        new_box.modification_time = 0
        new_box.content_size += 4
        new_box.time_scale = 0
        new_box.content_size += 4
        new_box.duration = 0
        new_box.content_size += 4
        new_box.language = 21956
        new_box.content_size += 2
        new_box.quality = 0
        new_box.content_size += 2

        return new_box

    def print_box(self, console):
        pass

    def get_metadata_string(self):
        return ""
        pass

    def save(self, in_fh, out_fh, delta):
        if (self.header_size == 16):
            out_fh.write(struct.pack(">I", 1))
            out_fh.write(struct.pack(">Q", self.size()))
            out_fh.write(self.name)
        elif(self.header_size == 8):
            out_fh.write(struct.pack(">I", self.size()))
            out_fh.write(self.name)
        out_fh.write(struct.pack(">I", 0)) # version flags
        out_fh.write(struct.pack(">I", self.creation_time)) # creation_time
        out_fh.write(struct.pack(">I", self.modification_time)) # modification_time
        out_fh.write(struct.pack(">I", self.time_scale)) # time_scale
        out_fh.write(struct.pack(">I", self.duration)) # duration
        out_fh.write(struct.pack(">H", self.language)) # language
        out_fh.write(struct.pack(">H", self.quality)) # quality

    def get_contents(self):
        data = b''
        data += struct.pack(">I", 0)
        data += struct.pack(">I", self.creation_time)
        data += struct.pack(">I", self.modification_time)
        data += struct.pack(">I", self.time_scale)
        data += struct.pack(">I", self.duration)
        data += struct.pack(">H", self.language)
        data += struct.pack(">H", self.quality)
        return data

class GmhdBox(box.Box):

    def __init__(self):
        box.Box.__init__(self)
        self.name = b'gmhd'
        self.header_size = 8
        self.version = 0
        self.gmin = None
        self.text = None

    def load(self, in_fh, position):
        if position is None:
            position = in_fh.tell()
            
        pp = in_fh.tell()

        in_fh.seek(position)
        header = in_fh.read(self.header_size)
        header_size = struct.unpack(">I", header[0:4])[0]
        header_name = header[4:8]
        if header_name == self.name and header_size > self.header_size:
            header = in_fh.read(self.header_size)
            header_size = struct.unpack(">I", header[0:4])[0]
            header_name = header[4:8]
            
            #print('#########')
            version_flags = in_fh.read(4)
            self.graphics_mode = struct.unpack(">H", in_fh.read(2))[0]
            self.op_color = struct.unpack(">LH", in_fh.read(6))[0]
            self.balance = struct.unpack(">H", in_fh.read(2))[0]
            self.reserved = struct.unpack(">H", in_fh.read(2))[0]
            #print(self.op_color, self.balance, self.reserved )
            
            #version_flags = in_fh.read(12)
            #print(version_flags)
            
            text_size = in_fh.read(4)
            self.text_size = struct.unpack(">L", text_size)[0]
            self.text_type = in_fh.read(4)
            self.text_data = None
            
            if self.text_type == b'tmcd':
                #print('&&&')
                self.tmcd_1 = struct.unpack(">i", in_fh.read(4))[0]
                self.tmcd_2 = in_fh.read(4)
                #print(self.tmcd_1, self.tmcd_2)
                
                if self.tmcd_2 == b'tcmi':
                    version_flags = in_fh.read(4)
                    text_font = struct.unpack(">H", in_fh.read(2))[0]
                    text_face = struct.unpack(">H", in_fh.read(2))[0]
                    text_size = struct.unpack(">H", in_fh.read(2))[0]
                    text_reserved = struct.unpack(">H", in_fh.read(2))[0]
                    text_color = in_fh.read(6)
                    text_background = in_fh.read(6)
                    p = in_fh.tell()
                    text_font_name = in_fh.read(self.tmcd_1 - 32)
                    
                    
                    #print(text_font, text_size, text_font_name)
                    
                
                
            else:
                self.text_data = in_fh.read(self.text_size-8)
            #print(self.text_size, self.text_type,self.text_data)
            
            
            
            in_fh.seek(pp)
            z = in_fh.read(50)
            #print('****', z)
            """size = in_fh.read(4)
            size = struct.unpack(">L", size)[0]
            name = in_fh.read(4)
            z = in_fh.read(header_size-16)
            print(z, size, name, header_size)
            version_flags = in_fh.read(4)
            number_of_entries = in_fh.read(4)
            number_of_entries = struct.unpack(">L", number_of_entries)[0]
            print('header_size', header_size)
            print('number_of_entries', number_of_entries)"""

    @staticmethod
    def create():
        new_box = GmhdBox()
        new_box.header_size = 8
        new_box.name = b'gmhd'
        new_box.version = 0                     # uint8
        """new_box.content_size += 4               # uint8

        new_box.content_size += 4
        
        new_box.content_size += 4

        new_box.content_size += 4

        new_box.content_size += 4

        new_box.content_size += 4"""

        return new_box

    def print_box(self, console):
        pass

    def get_metadata_string(self):
        return ""
        pass

    def save(self, in_fh, out_fh, delta):
        if (self.header_size == 16):
            out_fh.write(struct.pack(">I", 1))
            out_fh.write(struct.pack(">Q", self.size()))
            out_fh.write(self.name)
        elif(self.header_size == 8):
            out_fh.write(struct.pack(">I", self.size()))
            out_fh.write(self.name)
        """out_fh.write(struct.pack(">I", 0)) # version flags
        out_fh.write(struct.pack(">L", 1)) # number of entries
        out_fh.write(struct.pack(">L", self.data_size)) # number of entries
        print('!!!!', self.data_format, self.data_size, self.format_data)
        out_fh.write(self.data_format)
        if self.format_data:
            out_fh.write(self.format_data)
        else:
            out_fh.write(struct.pack(">I", 0)) 
            out_fh.write(struct.pack(">I", 1)) """

class GminBox(box.Box):

    def __init__(self):
        box.Box.__init__(self)
        self.name = b'gmin'
        self.header_size = 8
        self.version = 0
        self.extra_data = None

    def load(self, in_fh, position):
        if position is None:
            position = in_fh.tell()

        in_fh.seek(position)
        header = in_fh.read(self.header_size)
        header_size = struct.unpack(">I", header[0:4])[0]
        header_name = header[4:8]
        if header_name == self.name and header_size > self.header_size:
            version_flags = in_fh.read(4)
            graphics_mode = in_fh.read(2)
            op_color = in_fh.read(6)
            balance = in_fh.read(2)
            reserved = in_fh.read(2)

    @staticmethod
    def create():
        new_box = GminBox()
        new_box.header_size = 8
        new_box.name = b'gmin'
        new_box.version = 0                     # uint8
        new_box.content_size += 4               # uint8

        new_box.content_size += 2
        
        new_box.content_size += 6

        new_box.content_size += 2

        new_box.content_size += 2

        return new_box

    def print_box(self, console):
        pass

    def get_metadata_string(self):
        return ""
        pass

    def save(self, in_fh, out_fh, delta):
        if (self.header_size == 16):
            out_fh.write(struct.pack(">I", 1))
            out_fh.write(struct.pack(">Q", self.size()))
            out_fh.write(self.name)
        elif(self.header_size == 8):
            out_fh.write(struct.pack(">I", self.size()))
            out_fh.write(self.name)
        out_fh.write(struct.pack(">I", 0)) 
        out_fh.write(struct.pack(">H", 0)) 
        out_fh.write(struct.pack(">LH", 0, 0)) 
        out_fh.write(struct.pack(">H", 0)) 
        out_fh.write(struct.pack(">H", 0)) 
        if self.extra_data:
            out_fh.write(self.extra_data)

class TkhdBox(box.Box):

    def __init__(self):
        box.Box.__init__(self)
        self.name = constants.TAG_TKHD
        self.header_size = 8
        self.version = 0
        self.flags = 0
        self.creation_time = 0
        self.modification_time = 0
        self.track_id = 0
        self.reserved = 0
        self.duration = 0
        self.reserved1 = 0
        self.layer = 0
        self.alternate_group = 0
        self.volume = 0
        self.reserved2 = 0
        self.matrix_structure = 0
        self.track_width = 0
        self.track_height = 0

    def load(self, in_fh, position):
        if position is None:
            position = in_fh.tell()

        total_bytes_read = 0

        in_fh.seek(position)
        header = in_fh.read(self.header_size)
        header_size = struct.unpack(">I", header[0:4])[0]
        header_name = header[4:8]
        
        if header_name == self.name:
            version_flag = in_fh.read(4)
            self.creation_time = struct.unpack(">I", in_fh.read(4))[0]
            #self.creation_time = since1904(self.creation_time)
            self.modification_time = struct.unpack(">I", in_fh.read(4))[0]
            #self.modification_time = since1904(self.modification_time)
            track_id = struct.unpack(">I", in_fh.read(4))[0]
            self.track_id = track_id
            self.reserved = struct.unpack(">d", in_fh.read(8))[0]
            duration = struct.unpack(">I", in_fh.read(4))[0]
            self.duration = duration
            self.reserved1 = struct.unpack(">I", in_fh.read(4))[0]
            layer = struct.unpack(">H", in_fh.read(2))[0]
            self.layer = layer
            alternate_group = struct.unpack(">H", in_fh.read(2))[0]
            self.alternate_group = alternate_group
            volume = struct.unpack(">H", in_fh.read(2))[0]
            self.volume = volume
            self.reserved2 = struct.unpack(">H", in_fh.read(2))[0]
            matrix_structure = struct.unpack(">IIIIIIIII", in_fh.read(36))[0]
            self.matrix_structure = matrix_structure
            track_width = struct.unpack(">I", in_fh.read(4))[0]
            self.track_width = track_width
            track_height = struct.unpack(">I", in_fh.read(4))[0]
            self.track_height = track_height

    def getValues(self):
        return {
            'creation_time': self.creation_time,
            'modification_time': self.modification_time,
            'track_id': self.track_id,
            'reserved': self.reserved,
            'duration': self.duration,
            'reserved1': self.reserved1,
            'layer': self.layer,
            'alternate_group': self.alternate_group,
            'volume': self.volume,
            'reserved2': self.reserved2,
            'matrix_structure': self.matrix_structure,
            'track_width': self.track_width,
            'track_height': self.track_height,
        }

    @staticmethod
    def create():
        new_box = TkhdBox()
        new_box.header_size = 8
        new_box.name = constants.TAG_TKHD
        new_box.version = 0                     # uint8
        new_box.content_size += 4               # uint8

        new_box.creation_time = 0
        new_box.content_size += 4
        new_box.modification_time = 0
        new_box.content_size += 4
        new_box.track_id = 2
        new_box.content_size += 4
        new_box.reserved = 0
        new_box.content_size += 8
        new_box.duration = 2200
        new_box.content_size += 4
        new_box.reserved1 = 0
        new_box.content_size += 4
        new_box.layer = 0
        new_box.content_size += 2
        new_box.alternate_group = 0
        new_box.content_size += 2
        new_box.volume = 100
        new_box.content_size += 2
        new_box.reserved2 = 0
        new_box.content_size += 2
        new_box.matrix_structure = 65536
        new_box.content_size += 36
        new_box.track_width = 0
        new_box.content_size += 4
        new_box.track_height = 0
        new_box.content_size += 4

        return new_box

    def print_box(self, console):
        pass

    def get_metadata_string(self):
        return ""
        pass

    def save(self, in_fh, out_fh, delta):
        if (self.header_size == 16):
            out_fh.write(struct.pack(">I", 1))
            out_fh.write(struct.pack(">Q", self.size()))
            out_fh.write(self.name)
        elif(self.header_size == 8):
            out_fh.write(struct.pack(">I", self.size()))
            out_fh.write(self.name)
            
        out_fh.write(struct.pack(">b", 0)) # version flags
        out_fh.write(struct.pack(">bbb", 0x000001, 0x000002, 0x000004)) # version flags
        out_fh.write(struct.pack(">I", self.creation_time )) # creation time
        out_fh.write(struct.pack(">I", self.modification_time)) # modification time
        out_fh.write(struct.pack(">I", self.track_id )) # track_id
        out_fh.write(struct.pack(">L", self.reserved)) # reserved
        out_fh.write(struct.pack(">I", self.duration)) # duration
        out_fh.write(struct.pack(">Q", self.reserved1)) # reserved
        out_fh.write(struct.pack(">H", self.layer)) # layer
        out_fh.write(struct.pack(">H", self.alternate_group)) # alternate_group
        out_fh.write(struct.pack(">H", self.volume)) # volume
        out_fh.write(struct.pack(">H", self.reserved2)) # reserved
        
        out_fh.write(struct.pack(">i", 0))
        out_fh.write(struct.pack(">I", 0))
        out_fh.write(struct.pack(">I", 0))
        out_fh.write(struct.pack(">I", 0))
        out_fh.write(struct.pack(">I", 0))
        out_fh.write(struct.pack(">I", 0))
        out_fh.write(struct.pack(">I", 0))
        out_fh.write(struct.pack(">I", 0))
        out_fh.write(struct.pack(">I", 0))

        out_fh.write(struct.pack(">I", self.track_width)) # track_width
        out_fh.write(struct.pack(">I", self.track_height)) # track_height

    def get_contents(self):
        data = b''
            
        data += struct.pack(">b", 0)
        data += struct.pack(">bbb", 0x000001, 0x000002, 0x000004)
        data += struct.pack(">I", self.creation_time )
        data += struct.pack(">I", self.modification_time)
        data += struct.pack(">I", self.track_id )
        data += struct.pack(">L", 0)
        data += struct.pack(">I", self.duration)
        data += struct.pack(">Q", 0)
        data += struct.pack(">H", self.layer)
        data += struct.pack(">H", self.alternate_group)
        data += struct.pack(">H", self.volume)
        data += struct.pack(">H", 0)
        
        data += struct.pack(">i", 0)
        data += struct.pack(">I", 0)
        data += struct.pack(">I", 0)
        data += struct.pack(">I", 0)
        data += struct.pack(">I", 0)
        data += struct.pack(">I", 0)
        data += struct.pack(">I", 0)
        data += struct.pack(">I", 0)
        data += struct.pack(">I", 0)

        data += struct.pack(">I", self.track_width)
        data += struct.pack(">I", self.track_height)
        return data

class MvhdBox(box.Box):

    def __init__(self):
        box.Box.__init__(self)
        self.name = constants.TAG_MVHD
        self.header_size = 8
        self.version = 0
        self.creation_time = 0
        self.modification_time = 0
        self.timescale = 0
        self.duration = 0
        self.preferred_rate = 0
        self.preferred_volume = 0
        self.reserved = 0
        self.matrix_structure = 0
        self.preview_time = 0
        self.preview_duration = 0
        self.poster_time = 0
        self.selection_time = 0
        self.selection_duration = 0
        self.current_time = 0
        self.next_track_id = 0

    def load(self, in_fh, position):
        
        getcontext().prec = 2
        if position is None:
            position = in_fh.tell()

        total_bytes_read = 0

        in_fh.seek(position)
        header = in_fh.read(self.header_size)
        header_size = struct.unpack(">I", header[0:4])[0]
        header_name = header[4:8]
        if header_name == self.name:
            version_flag = in_fh.read(4)
            self.creation_time = struct.unpack(">I", in_fh.read(4))[0]
            self.creation_time = since1904(self.creation_time)
            self.modification_time = struct.unpack(">I", in_fh.read(4))[0]
            self.modification_time = since1904(self.modification_time)
            self.timescale = struct.unpack(">L", in_fh.read(4))[0]
            self.duration = struct.unpack(">L", in_fh.read(4))[0]
            self.preferred_rate = struct.unpack(">L", in_fh.read(4))[0] / (2**15)

            self.preferred_volume = struct.unpack(">H", in_fh.read(2))[0]
            self.reserved = in_fh.read(10)
            self.matrix_structure = in_fh.read(36)
            self.preview_time = struct.unpack(">I", in_fh.read(4))[0]
            self.preview_duration = struct.unpack(">I", in_fh.read(4))[0]
            self.poster_time = struct.unpack(">I", in_fh.read(4))[0]
            self.selection_time = struct.unpack(">I", in_fh.read(4))[0]
            self.selection_duration = struct.unpack(">I", in_fh.read(4))[0]
            self.current_time = struct.unpack(">I", in_fh.read(4))[0]
            self.next_track_id = struct.unpack(">I", in_fh.read(4))[0]

    def getValues(self):
        return {
            'timescale': self.timescale,
            'duration': self.duration,
            'preferred_rate': self.preferred_rate,
            'preferred_volume': self.preferred_volume,
            'preview_time': self.preview_time,
            'preview_duration': self.preview_duration,
            'poster_time': self.poster_time,
            'selection_time': self.selection_time,
            'selection_duration': self.selection_duration,
            'current_time': self.current_time,
            'next_track_id': self.next_track_id,
        }


    @staticmethod
    def create():
        new_box = MvhdBox()
        new_box.header_size = 8
        new_box.name = constants.TAG_MVHD
        new_box.version = 0                     # uint8
        new_box.content_size += 1               # uint8
        return new_box

    def print_box(self, console):
        pass

    def get_metadata_string(self):
        return ""
        pass

    def save(self, in_fh, out_fh, delta):
        pass

class EdtsBox(container.Container):

    def __init__(self):
        container.Container.__init__(self)
        self.name = constants.TAG_EDTS
        self.header_size = 8

    def load(self, in_fh, position):
        if position is None:
            position = in_fh.tell()

        in_fh.seek(position)
        z = in_fh.read(32)
        in_fh.seek(position)

        header = in_fh.read(self.header_size)
        header_size = struct.unpack(">I", header[0:4])[0]
        header_name = header[4:8]

        header = in_fh.read(self.header_size)
        header_size = struct.unpack(">I", header[0:4])[0]
        header_name = header[4:8]

        header = in_fh.read(4)
        header = in_fh.read(4)
        header_size = struct.unpack(">I", header[0:4])[0]

        header = in_fh.read(4)
        header_size = struct.unpack(">L", header[0:4])[0]

        header = in_fh.read(4)
        header_size = struct.unpack(">L", header[0:4])[0]

        header = in_fh.read(4)
        header_size = struct.unpack(">L", header[0:4])[0]


    @staticmethod
    def create():
        new_box = EdtsBox()
        new_box.header_size = 8
        new_box.name = constants.TAG_EDTS
        elst = ElstBox.create()
        new_box.contents.append(elst)
        return new_box

    def print_box(self, console):
        pass

    def get_metadata_string(self):
        return ""
        pass

    def save(self, in_fh, out_fh, delta):
        pass

class ElstBox(box.Box):

    def __init__(self):
        box.Box.__init__(self)
        self.name = b'elst'
        self.header_size = 8
        self.version = 0
        self.number_of_entries = 0
        self.entries = []
        self.track_duration = 0
        self.media_time = 0
        self.media_rate = 0
    def load(self, in_fh, position):
        if position is None:
            position = in_fh.tell()

        total_bytes_read = 0

        in_fh.seek(position)
        header = in_fh.read(self.header_size)
        header_size = struct.unpack(">I", header[0:4])[0]
        header_name = header[4:8]
        if header_name == self.name:
            header = in_fh.read(self.header_size)
            elst_size = struct.unpack(">I", header[0:4])[0]
            elst_name = header[4:8]
            version_flag = in_fh.read(4)
            number_of_entries = struct.unpack(">I", in_fh.read(4))[0]
            self.number_of_entries = number_of_entries
            for i in range(0, self.number_of_entries):
                track_duration = struct.unpack(">I", in_fh.read(4))[0]
                media_time = struct.unpack(">I", in_fh.read(4))[0]
                media_rate = struct.unpack(">I", in_fh.read(4))[0]
                self.entries.append([track_duration, media_time, media_rate])

    @staticmethod
    def create():
        new_box = ElstBox()
        new_box.header_size = 8
        new_box.name = b'elst'
        new_box.version = 0                     # uint8
        new_box.content_size += 4               # uint8
        new_box.number_of_entries = 1
        new_box.content_size += 4
        new_box.track_duration = 0
        new_box.content_size += 4
        new_box.media_time = 0
        new_box.content_size += 4
        new_box.media_rate = 65536
        new_box.content_size += 4
        return new_box

    def print_box(self, console):
        pass

    def get_metadata_string(self):
        return ""
        pass

    def save(self, in_fh, out_fh, delta):
        if (self.header_size == 16):
            out_fh.write(struct.pack(">I", 1))
            out_fh.write(struct.pack(">Q", self.size()))
            out_fh.write(self.name)
        elif(self.header_size == 8):
            out_fh.write(struct.pack(">I", self.size()))
            out_fh.write(self.name)
        out_fh.write(struct.pack(">I", self.version)) # version flags
        out_fh.write(struct.pack(">I", self.number_of_entries)) # version flags
        out_fh.write(struct.pack(">I", self.track_duration)) # version flags
        out_fh.write(struct.pack(">I", self.media_time)) # version flags
        out_fh.write(struct.pack(">I", self.media_rate)) # version flags

class DinfBox(box.Box):

    def __init__(self):
        box.Box.__init__(self)
        self.name = b"dinf"
        self.header_size = 8
        self.version = 0

    def load(self, in_fh, position):
        if position is None:
            position = in_fh.tell()
        total_bytes_read = 0
        in_fh.seek(position)
        header = in_fh.read(self.header_size)
        header_size = struct.unpack(">I", header[0:4])[0]
        header_name = header[4:8]
        if header_name == self.name:
            z=in_fh.read(self.header_size)
            z = in_fh.read(4)
            z = struct.unpack(">I", z)[0]
            z = in_fh.read(4)
            z = struct.unpack(">I", z)[0]


    @staticmethod
    def create():
        new_box = SA3DBox()
        new_box.header_size = 8
        new_box.name = b"dinf"
        new_box.version = 0                     # uint8
        new_box.content_size += 1               # uint8
        return new_box

    def print_box(self, console):
        pass

    def get_metadata_string(self):
        return ""
        pass

    def save(self, in_fh, out_fh, delta):
        pass

class MakeBox(box.Box):

    def __init__(self):
        box.Box.__init__(self)
        self.name = b"dinf"
        self.header_size = 8
        self.version = 0

    def load(self, in_fh, position):
        if position is None:
            position = in_fh.tell()
        total_bytes_read = 0
        in_fh.seek(position)
        header = in_fh.read(self.header_size)
        header_size = struct.unpack(">I", header[0:4])[0]
        header_name = header[4:8]
        if header_name == self.name:
            pass


    @staticmethod
    def create():
        new_box = MakeBox()
        new_box.header_size = 8
        new_box.name = b"dinf"
        new_box.version = 0                     # uint8
        new_box.content_size += 1               # uint8
        return new_box

    def print_box(self, console):
        pass

    def get_metadata_string(self):
        return ""
        pass

    def save(self, in_fh, out_fh, delta):
        pass

class ModelBox(box.Box):

    def __init__(self):
        box.Box.__init__(self)
        self.name = b"dinf"
        self.header_size = 8
        self.version = 0

    def load(self, in_fh, position):
        if position is None:
            position = in_fh.tell()
        total_bytes_read = 0
        in_fh.seek(position)
        header = in_fh.read(self.header_size)
        header_size = struct.unpack(">I", header[0:4])[0]
        header_name = header[4:8]
        if header_name == self.name:
            pass


    @staticmethod
    def create():
        new_box = ModelBox()
        new_box.header_size = 8
        new_box.name = b"dinf"
        new_box.version = 0                     # uint8
        new_box.content_size += 1               # uint8
        return new_box

    def print_box(self, console):
        pass

    def get_metadata_string(self):
        return ""
        pass

    def save(self, in_fh, out_fh, delta):
        pass

class MetaBox(box.Box):

    def __init__(self):
        box.Box.__init__(self)
        self.name = b"meta"
        self.header_size = 8
        self.version = 0
        self.hdlr = HdlrBox()
        self.ilst = IlstBox()
        self.contents = []

    def load(self, in_fh, position):
        if position is None:
            position = in_fh.tell()
        total_bytes_read = 0
        in_fh.seek(position)
        header = in_fh.read(self.header_size)
        header_size = struct.unpack(">I", header[0:4])[0]
        header_name = header[4:8]
        if header_name == self.name:
            version_flags = struct.unpack(">L", in_fh.read(4))[0]
            hdlr = HdlrBox()
            ilst = IlstBox()

            for i in range(0, 10):
                position = in_fh.tell()
                b = in_fh.read(self.header_size)
                if b != b'':
                    b_size = struct.unpack(">I", b[0:4])[0]
                    b_name = b[4:8]
                    if b_name == b"hdlr":
                        hdlr.load(in_fh, position)
                        self.contents.append(hdlr)
                    if b_name == b"ilst":
                        ilst.load(in_fh, position)
                        self.contents.append(ilst)
                    in_fh.seek(position+b_size)


            

    @staticmethod
    def create():
        new_box = MetaBox()
        new_box.header_size = 8
        new_box.name = b"meta"
        new_box.version = 0                     # uint8
        new_box.content_size += 1               # uint8
        return new_box

    def print_box(self, console):
        pass

    def get_metadata_string(self):
        return ""
        pass

    def save(self, in_fh, out_fh, delta):
        pass

class TrakAtom():
    trak_type = None
    tkhd = TkhdBox()
    edts = EdtsBox()
    mdhd = MdhdBox()
    hdlr = HdlrBox()
    stsd = StsdBox()
    stts = SttsBox()
    stsc = StscBox()
    stsz = StszBox()
    stco = StcoBox()
    co64 = Co64Box()
    mvhd = MvhdBox()
    meta = MetaBox()

    def get_type(self):
        return '{}'.format(self.trak_type.decode('utf-8'))

    def getValues(self):
        return {
            'trak_type': self.trak_type.decode('utf-8'),
            'tkhd': self.tkhd.getValues(),
            #'edts': self.edts.getValues(),
            'mdhd': self.mdhd.getValues(),
            'hdlr': self.hdlr.getValues(),
            'stts': self.stts.getValues(),
            'stsc': self.stsc.getValues(),
            'stsz': self.stsz.getValues(),
            'stco': self.stco.getValues(),
            'co64': self.co64.getValues(),
            #'meta': self.meta.getValues()
        }

class MoovAtom():
    mvhd = MvhdBox()
    traks = []

class Mp4Atom():
    moov = MoovAtom()
    metadata_identifier = b''
    metadata_track = -1
    tmcd_track = -1
    
    def __init__(self):
        self.moov.traks = []
    
    def read_atoms(self, f, mpeg4_file_structure):
        #mpeg4_file_structure.print_structure()
        for content in mpeg4_file_structure.contents:
            if content.name == b"moov":
                for moov_content in content.contents:
                    if moov_content.name == b"trak":
                        trak = self.parse_trak_atom(f, moov_content)
                        self.moov.traks.append(trak)
                    elif moov_content.name == b"mvhd":
                        self.moov.mvhd = MvhdBox()
                        self.moov.mvhd.load(f, moov_content.position)

    def parse_trak_atom(self, f, mpeg4):
        metadata_identifiers = [b'camm', b'gpmd']
        trak = TrakAtom()
        for content in mpeg4.contents:
            if content.name == b"tkhd":
                trak.tkhd = TkhdBox()
                trak.tkhd.load(f, content.position)
            elif content.name == b"mdia":
                
                for mdia_content in content.contents:
                    
                    if mdia_content.name == b"mdhd":
                        trak.mdhd = MdhdBox()
                        trak.mdhd.load(f, mdia_content.position)
                    elif mdia_content.name == b"hdlr":
                        trak.hdlr = HdlrBox()
                        trak.hdlr.load(f, mdia_content.position)
                    elif mdia_content.name == b"minf":
                        for minf_content in mdia_content.contents:
                            if minf_content.name == b"dinf":
                                trak.dinf = DinfBox()
                                trak.dinf.load(f, minf_content.position)
                            elif minf_content.name == b"gmhd":
                                #print('##################')
                                gmhd = GmhdBox()
                                gmhd.load(f, minf_content.position)
                                #print('##################')
                            elif minf_content.name == b"stbl":
                                for stbl_content in minf_content.contents:
                                    
                                    if stbl_content.name == b"stsd":
                                        trak.stsd  = StsdBox()
                                        trak.stsd.load(f, stbl_content.position)
                                        for stbl_content in stbl_content.contents:
                                            trak.trak_type = stbl_content.name
                                            if trak.trak_type in metadata_identifiers:
                                                self.metadata_identifier = trak.trak_type
                                                
                                    if stbl_content.name == b"stts":
                                        trak.stts  = SttsBox()
                                        trak.stts.load(f, stbl_content.position)
                                    if stbl_content.name == b"stsc":
                                        trak.stsc  = StscBox()
                                        trak.stsc.load(f, stbl_content.position)
                                    if stbl_content.name == b"stsz":
                                        trak.stsz  = StszBox()
                                        trak.stsz.load(f, stbl_content.position)
                                    if stbl_content.name == b"stco":
                                        trak.stco = StcoBox()
                                        trak.stco.load(f, stbl_content.position)
                                    if stbl_content.name == b"co64":
                                        trak.co64 = Co64Box()
                                        trak.co64.load(f, stbl_content.position)

        return trak

    def get_metadata_track(self, metadata_identifier):
        values = {}
        t = None
        for trak in self.moov.traks:
            if metadata_identifier == trak.trak_type:
                t = trak
                break
        return t
        
    def get_video_metadata(self):
        values = []
        for trak in self.moov.traks:
            trak_values = trak.getValues()
            if 'creation_time' in trak_values['tkhd']:
                trak_values['tkhd']['creation_time'] = ''
            if 'modification_time' in trak_values['tkhd']:
                trak_values['tkhd']['modification_time'] = ''
            if 'reserved' in trak_values['tkhd']:
                trak_values['tkhd']['reserved'] = ''
            if 'reserved1' in trak_values['tkhd']:
                trak_values['tkhd']['reserved1'] = ''
            if 'reserved2' in trak_values['tkhd']:
                trak_values['tkhd']['reserved2'] = ''
            trak_values['hdlr'] = {
                'subtype_metadata_type': trak_values['hdlr']['subtype_metadata_type'].decode('utf-8', 'ignore')
            }
            values.append(trak_values)
        return values

    def __get_sample_chunks(self, trak):
        stsc_chunks = []
        last_chunk = None
        for chunk in trak.stsc.frames:
            if last_chunk:
                diff = chunk[0] - last_chunk[0] - 1
                if diff > 0:
                    for i in range(0, diff):
                       stsc_chunks.append(last_chunk[1]) 
            stsc_chunks.append(chunk[1]) 
            last_chunk = chunk
        return stsc_chunks

    def __get_offset_data(self, f, trak):
        offset_data = []
        offsets = []
        if trak is None:
            return offset_data
        if trak.co64 is not None:
            if len(trak.co64.offsets) > 0:
                offsets = trak.co64.offsets
        if len(offsets) == 0:
            if trak.stco is not None:
                if len(trak.stco.offsets) > 0:
                    offsets = trak.stco.offsets
        offsets_len = len(offsets)
        sample_chunks = self.__get_sample_chunks(trak)
        chunks_len = len(sample_chunks)
        sizes_len = len(trak.stsz.sizes)
        for i in range(0, offsets_len):
            offset = offsets[i]
            chunks = 1
            if i < chunks_len:
                chunks = sample_chunks[i]
            k = i+chunks
            if k <= sizes_len:
                for j in range(i, k):
                    size = trak.stsz.sizes[j]
                    f.seek(offset)
                    data = f.read(size)
                    if data:
                        offset_data.append(data)
                    offset += size
        return offset_data

    def get_camm_raw_metadata(self, f):
        metadata = []
        trak = self.get_metadata_track(b'camm')
        offset_data = self.__get_offset_data(f, trak)
        for od in offset_data:
            metadata.append(od)
        return metadata

    def get_camm_metadata(self, f):
        metadata = []
        trak = self.get_metadata_track(b'camm')
        offset_data = self.__get_offset_data(f, trak)
        for od in offset_data:
            camm = CammMetadata()
            data = camm.read(od)
            if data:
                metadata.append(data)
        return metadata

    def get_gpmd_raw_metadata(self, f):
        metadata = []
        trak = self.get_metadata_track(b'gpmd')
        offset_data = self.__get_offset_data(f, trak)
        for od in offset_data:
            metadata.append(od)
        return metadata

    """def get_gpmd_metadata(self, f):
        metadata = []
        trak = self.get_metadata_track(b'gpmd')
        offset_data = self.__get_offset_data(f, trak)
        for od in offset_data:
            gpmd = GpmdMetadata()
            data = gpmd.read(od)
            if data:
                metadata.append(data)
        return metadata"""

    def create_camm_metadata_atoms(self, f, mdata, framerate):
        mp4_st = mpeg4_container.load(f)
        mp4_st.print_structure()
        mp4 = Mp4Atom()
        mp4.read_atoms(f, mp4_st)
        ftyp = None
        free = None
        mdat = None
        moov = None
        new_contents = []
        for c in mp4_st.contents:
            if c.name == b'mdat':
                mdat = c
            elif c.name == b'moov':
                moov = c
            elif c.name == b'ftyp':
                ftyp = c
            elif c.name == b'free':
                free = c
            else:
                new_contents.append(c)
        i = 1      
        d = 0
        data = b''
        times = [[1, 0]]
        sizes = []
        frames = []
        offsets = []
        framerate = framerate
        timescale = 90000
        mdat.header_size = 16
        mdat_size = mdat.size()-8
        print('mdat_size', mdat_size)
        m_pos = mdat.position + mdat_size+8
        print('m_pos', m_pos)
        metadatas = mdata['metadata']
        metadata_duration = mdata['duration']
        start_time = int(since1904_to_seconds(mdata['start_time']))

        mp4_st.resize()
        moov.resize()
        mp4_st.resize()
        for m in metadatas:
            data += m['metadata']
            l = len(m['metadata'])
            d = int(timescale/framerate)
            times.append([1, d])
            sizes.append(l)
            offsets.append(m_pos)
            print('m_pos', m_pos, m['metadata'])
            m_pos += l
            frames.append([i,1, 1])
            i += 1

        mdat.content_size = mdat_size+len(data)
        mdat.data = data
        mp4_st.resize()

        stbl = mpeg.Container()
        stbl.header_size = 8
        stbl.name = b"stbl"

        stsd = StsdBox.create()
        stsd.data_size = 16
        stsd.data_format = b'camm'
        stsd.format_data = struct.pack(">I", 0)
        stsd.format_data += struct.pack(">I", 1)
        stbl.add(stsd)

        stts = SttsBox.create(times)
        stts.times = times 
        stbl.add(stts)
        mp4_st.resize()

        stsc = StscBox.create(frames)
        stsc.frames = frames 
        stbl.add(stsc)

        stsz = StszBox.create(sizes)
        stsz.sizes = sizes
        stbl.add(stsz)

        co64 = Co64Box.create(offsets)
        co64.offsets = offsets
        stbl.add(co64)
        stbl.resize()

        trak = mpeg.Container()
        trak.header_size = 8
        trak.name = b"trak"

        tkhd = TkhdBox.create()
        tkhd.creation_time = start_time
        tkhd.modification_time = start_time

        edts = EdtsBox.create()

        mdia = mpeg.Container()
        mdia.header_size = 8
        mdia.name = b"mdia"

        mdhd = MdhdBox.create()
        mdhd.time_scale = timescale
        mdhd.duration = int(metadata_duration * timescale)
        mdhd.creation_time = start_time
        mdhd.modification_time = start_time

        hdlr = HdlrBox.create()
        hdlr.subtype_metadata_type = b'\x00\x00\x00\x00camm\x00\x00\x00\x00'
        hdlr.content_size += 12
        hdlr.quicktime_component_reserved_flags_mask = b'CameraMetadataMotionHandler'
        hdlr.content_size += 27

        minf = mpeg.Container()
        minf.header_size = 8
        minf.name = b"minf"

        dinf = mpeg.Box()
        dinf.header_size = 8
        dinf.name = b"dinf"

        minf.add(stbl)
        mdia.add(mdhd)
        mdia.resize()
        mdia.add(hdlr)
        mdia.resize()
        mdia.add(minf)
        mdia.resize()
        trak.add(tkhd)
        trak.add(mdia)
        trak.resize()
        moov.contents.append(trak)
        mp4_st.resize()
        return mp4_st

    def create_gpmd_metadata_atoms(self, f, mdata, framerate):
        mp4_st = mpeg4_container.load(f)
        mp4_st.print_structure()
        mp4 = Mp4Atom()
        mp4.read_atoms(f, mp4_st)
        ftyp = None
        free = None
        mdat = None
        moov = None
        new_contents = []
        for c in mp4_st.contents:
            if c.name == b'mdat':
                mdat = c
            elif c.name == b'moov':
                moov = c
            elif c.name == b'ftyp':
                ftyp = c
            elif c.name == b'free':
                free = c
            else:
                new_contents.append(c)
        i = 1      
        d = 0
        data = b''
        times = [[1, 0]]
        sizes = []
        frames = []
        offsets = []
        framerate = framerate
        timescale = 1000
        metadatas = mdata['metadata']
        metadata_duration = mdata['duration']
        start_time = int(since1904_to_seconds(mdata['start_time']))

        mdat_size = mdat.size()-8
        
        print('mdat_size', mdat_size)
        m_pos = mdat.position + mdat_size+8
        print('pos', m_pos)

        mp4_st.resize()
        moov.resize()
        mp4_st.resize()
        for m in metadatas:
            
            data += m['metadata']
            l = len(m['metadata'])
            d = int(timescale/framerate)
            print('pos', m_pos, m['metadata'])
            times.append([1, d])
            sizes.append(l)
            offsets.append(m_pos)
            m_pos += l
            
            frames.append([i,1, 1])
            i += 1

        mdat.content_size = mdat_size+len(data)
        mdat.data = data
        mp4_st.resize()

        stbl = mpeg.Container()
        stbl.header_size = 8
        stbl.name = b"stbl"

        stsd = StsdBox.create()
        stsd.content_size += 4
        stsd.data_size = 20
        stsd.data_format = b'gpmd'
        stsd.format_data = struct.pack(">I", 0)
        stsd.format_data += struct.pack(">I", 1)
        stsd.format_data += struct.pack(">I", 0)
        stbl.add(stsd)

        stts = SttsBox.create(times)
        stts.times = times 
        stbl.add(stts)
        mp4_st.resize()

        stsc = StscBox.create(frames)
        stsc.frames = frames 
        stbl.add(stsc)

        stsz = StszBox.create(sizes)
        stsz.sizes = sizes
        stbl.add(stsz)
        
        stco = StcoBox.create(offsets)
        stco.offsets = offsets
        stbl.add(stco)
        stbl.resize()

        trak = mpeg.Container()
        trak.header_size = 8
        trak.name = b"trak"

        tkhd = TkhdBox.create()
        tkhd.creation_time = start_time
        tkhd.modification_time = start_time

        edts = EdtsBox.create()

        mdia = mpeg.Container()
        mdia.header_size = 8
        mdia.name = b"mdia"

        mdhd = MdhdBox.create()
        mdhd.time_scale = timescale
        mdhd.duration = int(metadata_duration * timescale)
        mdhd.creation_time = start_time
        mdhd.modification_time = start_time

        hdlr = HdlrBox.create()
        hdlr.quicktime_type = b'mhlrmeta'
        hdlr.content_size += 8
        hdlr.subtype_metadata_type = b'\x00\x00\x00\x00'
        hdlr.content_size += 4
        hdlr.quicktime_component_reserved_flags_mask = b'\x0bGoPro MET  '
        hdlr.content_size += 12

        gmin = GminBox.create()
        gmin.extra_data = b''
        gmin.extra_data += struct.pack(">L", 11)
        gmin.extra_data += b'gpmd'
        gmin.extra_data += b'\x00\x00\x00\x00'
        

        gmhd = mpeg.Container()
        gmhd.header_size = 8
        gmhd.name = b"gmhd"
        gmin.content_size += len(gmin.extra_data)
        
        gmhd.contents.append(gmin)
        gmhd.resize()
        

        minf = mpeg.Container()
        minf.header_size = 8
        minf.name = b"minf"

        dinf = mpeg.Box()
        dinf.header_size = 8
        dinf.name = b"dinf"

        minf.add(gmhd)
        minf.add(stbl)
        minf.resize()
        mdia.add(mdhd)
        mdia.resize()
        mdia.add(hdlr)
        mdia.resize()
        mdia.add(minf)
        mdia.resize()
        trak.add(tkhd)
        trak.add(mdia)
        trak.resize()

        moov.contents.append(trak)
        mp4_st.resize()
        return mp4_st

