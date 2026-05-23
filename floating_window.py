#!/usr/bin/env python3
import os
import shutil
import sys
import tkinter as tk

from aram_helper.app_state import AppStateService
from aram_helper.data_store import ChampionDataStore
from aram_helper.data_update import update_champion_data
from aram_helper.hotkeys import GlobalHotkeyService
from aram_helper.lcu_client import LcuClient
from aram_helper.ocr_service import HextechOcrService
from aram_helper.recommendations import RecommendationEngine
from aram_helper.ui import AramHelperApp


def resource_path(filename: str) -> str:
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


def data_file_path() -> str:
    if not getattr(sys, "frozen", False):
        return resource_path("champions_data.json")

    local_path = os.path.join(os.getcwd(), "champions_data.json")
    if not os.path.exists(local_path):
        shutil.copyfile(resource_path("champions_data.json"), local_path)
    return local_path


def main():
    data_path = data_file_path()
    root = tk.Tk()
    app = AramHelperApp(
        root=root,
        data_store=ChampionDataStore(data_path),
        state_service=AppStateService(LcuClient()),
        recommendation_engine=RecommendationEngine(),
        ocr_service_factory=HextechOcrService,
        update_data=lambda: update_champion_data(data_path, "https://hextech.dtodo.cn/zh-CN"),
        hotkey_service=GlobalHotkeyService(),
    )
    app.start()


if __name__ == "__main__":
    main()
