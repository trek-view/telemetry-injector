import os, sys, json, struct, time
from pathlib import Path

#Inspired from spatialmedia: https://github.com/google/spatial-media

class Box():
    def __init__(self):
        self.header_size = 8
        self.content_size = 0
        self.name = b''
        self.entries = []
    def load(self, f, pos, size):
        pass
    def create(self):
        pass
    def get_data(self):
        pass
    def get_values(self):
        pass
    def get_json_values(self):
        return {
            'name': str(self.name, 'utf-8'),
            'header_size': self.header_size,
            'content_size': self.content_size,
            'entries': self.entries,
            'total_values': len(self.entries),
        }

class StcoBox(Box):
    def __init__(self):
        Box.__init__(self)
        self.name = b'stco'
        self.total = 0
        self.entries = []
    def load(self, f, pos, size):
        f.seek(pos)
        version_flags = f.read(4)
        total = f.read(4)
        self.total = struct.unpack(">L", total)[0]
        d_size = self.header_size
        for i in range(0, self.total):
            offset = f.read(4)
            offset = struct.unpack(">L", offset)[0]
            self.entries.append(offset)
            d_size += 4
            if d_size > size:
                break
        self.content_size = d_size - self.header_size
    def create(self):
        pass
    @staticmethod
    def get_data(data):
        binary = b''
        binary += struct.pack(">L", 0)
        binary += struct.pack(">L", data['total_values'])
        for i in data['entries']:
            binary += struct.pack(">L", i)
        return binary
    def get_values(self):
        pass

class Co64Box(Box):
    def __init__(self):
        Box.__init__(self)
        self.name = b'stco'
        self.total = 0
        self.entries = []
    def load(self, f, pos, size):
        version_flags = f.read(4)
        total = f.read(4)
        self.total = struct.unpack(">L", total)[0]
        d_size = self.header_size
        for i in range(0, self.total):
            offset = f.read(8)
            offset = struct.unpack(">Q", offset)[0]
            self.entries.append(offset)
            d_size += 8
            if d_size > size:
                break
        self.content_size = d_size - self.header_size
    def create(self):
        pass
    @staticmethod
    def get_data(data):
        binary = b''
        binary += struct.pack(">L", 0)
        binary += struct.pack(">L", data['total_values'])
        for i in data['entries']:
            binary += struct.pack(">Q", i)
        return binary
    def get_values(self):
        pass

class SttsBox(Box):
    def __init__(self):
        Box.__init__(self)
        self.name = b'stts'
        self.total = 0
        self.entries = []
    def load(self, f, pos, size):
        version_flags = f.read(4)
        total = f.read(4)
        self.total = struct.unpack(">L", total)[0]
        d_size = self.header_size
        for i in range(0, self.total):
            t1 = struct.unpack(">L", f.read(4))[0]
            t2 = struct.unpack(">L", f.read(4))[0]
            self.entries.append([t1, t2])
            d_size += 4
            d_size += 4
            if d_size > size:
                break
        self.content_size = d_size - self.header_size
    def create(self):
        pass
    @staticmethod
    def get_data(data):
        binary = b''
        binary += struct.pack(">L", 0)
        binary += struct.pack(">L", data['total_values'])
        for i in data['entries']:
            binary += struct.pack(">L", i[0])
            binary += struct.pack(">L", i[1])
        return binary
    def get_values(self):
        pass

class StszBox(Box):
    def __init__(self):
        Box.__init__(self)
        self.name = b'stsz'
        self.total = 0
        self.entries = []
    def load(self, f, pos, size):
        version_flags = f.read(4)
        block_size = f.read(4)
        self.block_size = struct.unpack(">L", block_size)[0]
        total = f.read(4)
        self.total = struct.unpack(">L", total)[0]
        d_size = self.header_size
        for i in range(0, self.total):
            t1 = struct.unpack(">L", f.read(4))[0]
            self.entries.append(t1)
            d_size += 4
            if d_size > size:
                break
        self.content_size = d_size - self.header_size
    def create(self):
        pass
    @staticmethod
    def get_data(data):
        binary = b''
        binary += struct.pack(">L", 0)
        inary += struct.pack(">L", data['block_size'])
        binary += struct.pack(">L", data['total_values'])
        for i in data['entries']:
            binary += struct.pack(">L", i)
        return binary
    def get_values(self):
        pass

class StscBox(Box):
    def __init__(self):
        Box.__init__(self)
        self.name = b'stsc'
        self.total = 0
        self.entries = []
    def load(self, f, pos, size):
        version_flags = f.read(4)
        total = f.read(4)
        self.total = struct.unpack(">L", total)[0]
        d_size = self.header_size
        for i in range(0, self.total):
            t1 = struct.unpack(">L", f.read(4))[0]
            t2 = struct.unpack(">L", f.read(4))[0]
            t3 = struct.unpack(">L", f.read(4))[0]
            self.entries.append([t1, t2, t3])
            d_size += 4
            d_size += 4
            d_size += 4
            if d_size > size:
                break
        self.content_size = d_size - self.header_size
    def create(self):
        pass
    @staticmethod
    def get_data(data):
        binary = b''
        binary += struct.pack(">L", 0)
        binary += struct.pack(">L", data['total_values'])
        for i in data['entries']:
            binary += struct.pack(">L", i[0])
            binary += struct.pack(">L", i[1])
            binary += struct.pack(">L", i[2])
        return binary
    def get_values(self):
        pass

class StsdBox(Box):
    def __init__(self):
        Box.__init__(self)
        self.name = b'stsd'
        self.total = 0
        self.entries = []
    def load(self, f, pos, size):
        version_flags = f.read(4)
        total = f.read(4)
        self.total = struct.unpack(">L", total)[0]
        d_size = self.header_size
        for i in range(0, self.total):
            size = struct.unpack(">L", f.read(4))[0]
            data_format = f.read(4)
            additional_data = f.read(size-8)
            if data_format == b'camm' or data_format == b'gpmd':
                self.entries.append([
                    size,
                    data_format.decode('utf-8', 'backslashreplace'),
                    additional_data.decode('utf-8', 'backslashreplace'),
                ])
            else:
                self.entries.append([
                    size,
                    data_format.decode('utf-8', 'backslashreplace'),
                    additional_data.decode('utf-8', 'backslashreplace'),
                ])
            d_size += 4
            d_size += 4
            d_size += size-8
            if d_size > size:
                break
        self.content_size = d_size - self.header_size
    def create(self):
        pass
    @staticmethod
    def get_data(data):
        binary = b''
        return binary
    def get_values(self):
        pass

class DinfBox(Box):
    def __init__(self):
        Box.__init__(self)
        self.name = b'dinf'
        self.total = 0
        self.entries = []
    def load(self, f, pos, size):
        f.seek(pos)
        d_size = self.header_size
        dsize = struct.unpack(">I", f.read(4))[0]
        name = f.read(4)
        version = struct.unpack(">b", f.read(1))[0]
        flags = f.read(3)
        self.total = struct.unpack(">L", f.read(4))[0]
        data = {
            'size': dsize,
            'name': str(name, 'utf-8'),
            'version': int(version),
            'flags': str(flags, 'utf-8'),
            'data': [],
        }
        for i in range(0, self.total):
            _size = struct.unpack(">I", f.read(4))[0]
            _name = f.read(4)
            version = struct.unpack(">b", f.read(1))[0]
            flags = f.read(3)
            _data = f.read(_size-12)
            if len(data['data']) < 1:
                data['data'] = {}
            data['data'][i] = {
                'size': _size,
                'name': str(_name, 'utf-8'),
                'version': int(version),
                'flags': str(flags, 'utf-8'),
            }
            if _data != b'':
                data['data'][i]['data'] = str(_data, 'utf-8')

        self.entries = data

        self.content_size = size - self.header_size
    def create(self):
        pass
    @staticmethod
    def get_data(data):
        binary = b''
        return binary
    def get_values(self):
        pass

class HdlrBox(Box):
    def __init__(self):
        Box.__init__(self)
        self.name = b'hdlr'
        self.total = 0
        self.entries = []
    def load(self, f, pos, size):
        f.seek(pos)
        version_flags = f.read(4)
        component_type = f.read(4)
        component_sub_type = f.read(4)
        component_manufacturer = struct.unpack(">I", f.read(4))[0]
        component_flags = struct.unpack(">I", f.read(4))[0]
        component_flags_mask = struct.unpack(">I", f.read(4))[0]
        component_length = size - self.header_size - (6*4)
        component_name = f.read(component_length)
        self.content_size = component_length + 24
        self.entries = {
            "component_type": str(component_type, 'utf-8'),
            "component_sub_type": str(component_sub_type, 'utf-8'),
            "component_manufacturer": component_manufacturer,
            "component_flags": component_flags,
            "component_flags_mask": component_flags_mask,
            "component_name": str(component_name, 'utf-8'),
        }
    def create(self):
        pass
    @staticmethod
    def get_data(data):
        binary = b''
        binary += struct.pack(">L", 0)
        binary += struct.pack(">L", data['total_values'])
        for i in data['entries']:
            binary += struct.pack(">L", i[0])
            binary += struct.pack(">L", i[1])
        return binary
    def get_values(self):
        pass


__containers = [
    b'moov',
    b'trak',
    b'mdia',
    b'minf',
    b'stbl',
    b'uuid',
    b'wave',
    b'udta',
]

def get_data(atom):
    if atom['name'] == 'stco':
        return StcoBox.get_data(atom['data'])
    elif atom['name'] == 'stts':
        return SttsBox.get_data(atom['data'])
    elif atom['name'] == 'co64':
        return Co64Box.get_data(atom['data'])
    else:
        return b''

def read_childrens(f, pos, fsize, atom):
    f.seek(pos)
    data = None
    if atom == b'stco':
        stco = StcoBox()
        stco.load(f, pos, fsize)
        data = stco.get_json_values()
    elif atom == b'co64':
        co64 = Co64Box()
        co64.load(f, pos, fsize)
        data = co64.get_json_values()
    elif atom == b'stts':
        stts = SttsBox()
        stts.load(f, pos, fsize)
        data = stts.get_json_values()
    elif atom == b'stsz':
        stsz = StszBox()
        stsz.load(f, pos, fsize)
        data = stsz.get_json_values()
    elif atom == b'stsc':
        stsc = StscBox()
        stsc.load(f, pos, fsize)
        data = stsc.get_json_values()
    elif atom == b'stsd':
        stsd = StsdBox()
        stsd.load(f, pos, fsize)
        data = stsd.get_json_values()
    elif atom == b'dinf':
        dinf = DinfBox()
        dinf.load(f, pos, fsize)
        data = dinf.get_json_values()
    elif atom == b'hdlr':
        hdlr = HdlrBox()
        hdlr.load(f, pos, fsize)
        data = hdlr.get_json_values()
    else:
        n = [b'mdat']
        if atom not in n:
            try:
                data = f.read(fsize-8).decode('utf-8', 'backslashreplace')
            except:
                data = None
    
    return data

def read_atoms(f, pos, fsize):
    childrens = []
    while(pos < fsize):
        box_data = {
            'header_size': 8,
            'name': '',
            'size': 0,
            'type': 'container',
            'position': pos,
            'childrens': [],
            'data': {},
        }
        f.seek(pos)
        size = struct.unpack(">I", f.read(4))[0]
        atom = f.read(4)
        if size < 1:
            break
        if size == 1:
            size = struct.unpack(">Q", f.read(8))[0]
            box_data['header_size'] = 16
        box_data['size'] = size
        try:
            box_data['name'] = str(atom, 'utf-8')
        except:
            box_data['name'] = str(atom)
        pos = f.tell()
        atom_offset = pos + size - box_data['header_size']
        if atom_offset > fsize:
            break
        if atom in __containers:
            try:
                atom = str(atom, 'utf-8')
            except:
                atom = str(atom)
            atom_childrens = read_atoms(f, pos, atom_offset)
            box_data['childrens'] = atom_childrens
            childrens.append({ atom: box_data})
        else:
            box_data['type'] = 'box'
            try:
                _atom = str(atom, 'utf-8')
            except:
                _atom = str(atom)
            data = read_childrens(f, pos, size, atom)
            box_data['data'] = data
            childrens.append({ _atom: box_data})
        f.seek(atom_offset)
        
        pos = f.tell()

    return childrens

def main():
    video = sys.argv[1]
    vname = Path(video).name.replace(Path(video).suffix, '')
    with open(video, 'rb') as f:
        f.seek(0, 2)
        pos = 0
        fsize = f.tell()
        mp4_st = read_atoms(f, pos, fsize)
        with open('./{}.json'.format(vname), 'w') as jf:
            jf.write(json.dumps(mp4_st, indent=2))

if __name__ == "__main__":
    main()
