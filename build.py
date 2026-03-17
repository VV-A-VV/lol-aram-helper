#!/usr/bin/env python3
import PyInstaller.__main__
import os

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run([
    'floating_window.py',
    '--name=LOL_ARAM_Helper',
    '--onefile',
    '--windowed',
    '--add-data=champions_data.json;.',
    '--add-data=scraper.py;.',
    '--icon=NONE',
    '--clean',
])
