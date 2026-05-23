#!/usr/bin/env python3
import PyInstaller.__main__

PyInstaller.__main__.run([
    "floating_window.py",
    "--name=LOL_ARAM_Helper",
    "--onefile",
    "--windowed",
    "--add-data=champions_data.json;.",
    "--collect-all=rapidocr_onnxruntime",
    "--hidden-import=psutil",
    "--hidden-import=rapidocr_onnxruntime",
    "--hidden-import=mss",
    "--hidden-import=keyboard",
    "--hidden-import=cv2",
    "--hidden-import=numpy",
    "--icon=NONE",
    "--clean",
])
