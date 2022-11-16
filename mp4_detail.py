import os, sys, json, struct
from pathlib import Path

#Inspired from spatialmedia: https://github.com/google/spatial-media

class Box():
    def __init__(self):
        self.header_size = 8
        self.content_size = 0
        self.name = b''
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


__containers = [
    b'moov',
    b'meta',
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
    else:
        return b''

def read_childrens(f, pos, fsize, atom):
    data = None
    if atom == b'stco':
        stco = StcoBox()
        stco.load(f, pos, fsize)
        data = stco.get_json_values()
    elif atom == b'stts':
        stts = SttsBox()
        stts.load(f, pos, fsize)
        data = stts.get_json_values()
    f.seek(pos)
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
        if size == 1:
            size = struct.unpack(">Q", f.read(8))[0]
            box_data['header_size'] = 16
        atom = f.read(4)
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
    with open(video, 'rb') as f:
        f.seek(0, 2)
        pos = 0
        fsize = f.tell()
        mp4_st = read_atoms(f, pos, fsize)
        print(json.dumps(mp4_st, indent=2))

if __name__ == "__main__":
    main()
