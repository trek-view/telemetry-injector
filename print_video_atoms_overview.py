import sys, copy
from pathlib import Path
from spatialmedia import mpeg as mpeg4_container

filename = sys.argv[1]

with open(filename, "rb") as f:
    m = mpeg4_container.load(f)
    m.print_structure()
    