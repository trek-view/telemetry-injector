import os,re, sys, math, json, datetime, subprocess
from pathlib import Path 

from metadata.mp4 import Mp4Atom

from spatialmedia import mpeg as mpeg4_container

with open(sys.argv[1], "rb") as f:
    mp4_st = mpeg4_container.load(f)
    mp4 = Mp4Atom()
    mp4.read_atoms(f, mp4_st)
    metadata = mp4.get_camm_raw_metadata(f)
    for m in metadata:
        print('')
        print(m)
        print('')
    
    metadata = mp4.get_gpmd_raw_metadata(f)
    for m in metadata:
        print('')
        print(m)
        print('')
    
    mp4_st.print_structure()
    
    print(json.dumps(mp4.moov.mvhd.getValues(), indent=2))

    print('Metadata Track:')

    for trak in mp4.moov.traks:
        if (trak.trak_type == b'camm') or (trak.trak_type == b'gpmd'):
            z = trak.getValues()
            print(json.dumps(z, indent=2))
