#!/usr/bin/env python3

import os
import sys
import shutil


def main():
    if len(sys.argv) < 2:
        print('Need a folder name to be created as argument.')
        return
    folder = sys.argv[1]
    if os.path.exists(folder):
        print('Folder already exists. Aborting.')
        return
    os.mkdir(folder)
    slideshowfiles = os.listdir('slideshow')
    for sfile in slideshowfiles:
        shutil.move(os.path.join('slideshow', sfile),
                    os.path.join(folder, sfile))
    dummyslideshowfiles = os.listdir('dummyslideshow')
    for sfile in dummyslideshowfiles:
        shutil.copyfile(os.path.join('dummyslideshow', sfile),
                        os.path.join('slideshow', sfile))


if __name__ == '__main__':
    main()
