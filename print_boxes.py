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
    
    mp4_st.print_structure()

    print('Metadata Track:')

    for trak in mp4.moov.traks:
        if (trak.trak_type == b'camm') or (trak.trak_type == b'gpmd'):
            print('\n\tTkhd:')
            for k, v in trak.tkhd.getValues().items():
                print('\t {}: {}'.format(k, v))
            print('\n\tHdlr:')
            for k, v in trak.hdlr.getValues().items():
                print('\t {}: {}'.format(k, v))
            print('\n\tMdhd:')
            for k, v in trak.mdhd.getValues().items():
                print('\t {}: {}'.format(k, v))
            print('\n\tStsd:')
            for k, v in trak.stsd.getValues().items():
                print('\t {}: {}'.format(k, v))
    print('')
