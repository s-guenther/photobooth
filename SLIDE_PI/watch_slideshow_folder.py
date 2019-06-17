#!/usr/bin/env python3

import os
import time
from glob import glob

thisdir = os.getcwd()
os.chdir('/home/pi/slideshow')

while True:
    allfiles = os.listdir()
    dummyfiles = glob('dummy*')
    if not dummyfiles:
        break
    if len(allfiles) > 5:
        os.remove(dummyfiles.pop())
    time.sleep(1)

os.chdir(thisdir)
