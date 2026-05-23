# ARAM Helper Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the helper into clear modules that show champion tier, recommended augments, recommended items during champ select, then rank and annotate in-game augment choices for the selected champion.

**Architecture:** Keep the current Python desktop app and turn `floating_window.py` into a thin launcher/UI adapter. Move LCU access, champion data, recommendation ranking, OCR capture, and app state into independent modules under `aram_helper/`, each with unit tests. Use a queue plus Tk `after()` for thread-safe UI updates.

**Tech Stack:** Python 3.11, Tkinter, psutil, urllib/ssl, RapidOCR, mss, OpenCV, numpy, unittest, PyInstaller.

---

## Design

### Product Behavior

The app has two visible modes:

- Champ select: detect the local player's selected champion and bench champions from LCU, then show each champion's tier, win rate, ordered recommended augments, and recommended items.
- In game: keep the locked champion from champ select, detect when the user asks to scan augment choices, OCR the three augment names, match them against that champion's ordered recommendations, and label each choice with rank and recommendation level.

The first refactor does not try to automate mouse clicks or select augments. It only displays rankings and confidence.

### Data Contract

Champion data should be loaded through one repository interface, not opened directly from UI or OCR modules.

```json
{
  "last_update": "2026-03-17",
  "champions": {
    "876": {
      "name": "含羞蓓蕾 莉莉娅",
      "tier": "T1",
      "winrate": "59.09%",
      "augments": ["祖母的辣椒油", "红包", "咏叹奏鸣"],
      "items": ["法穿鞋", "卢登", "影焰", "金身", "虚空", "帽子"]
    }
  }
}
```

During migration, existing `augments` remains valid and is treated as an ordered recommendation list. The updater should later expand this list beyond the current top 3 when the source page exposes more rows. Ranking logic must work with any ordered list length.

### Module Boundaries

- `aram_helper/models.py`: dataclasses and enums only.
- `aram_helper/data_store.py`: load/save/migrate `champions_data.json`.
- `aram_helper/lcu_client.py`: discover LCU port/token and call LCU endpoints.
- `aram_helper/recommendations.py`: rank augments and normalize OCR text.
- `aram_helper/app_state.py`: convert LCU responses into UI snapshots.
- `aram_helper/ocr_service.py`: capture configured screen regions and run OCR.
- `aram_helper/ui.py`: Tk widgets and rendering only.
- `floating_window.py`: import `AramHelperApp` and run it.

### Error Handling

LCU connection failures return typed disconnected state instead of raising through the UI thread. Missing data returns a champion card with `ID:<champion_id>` and empty recommendations. OCR failures return an error result shown in the OCR panel without killing the app.

### Verification Strategy

Unit tests cover data loading, ranking, text normalization, LCU response parsing, and app-state transitions. GUI verification is a smoke run through `py_compile` plus a manual local run because Tkinter UI behavior is visual and depends on LOL client state.

---

## File Structure

- Create: `aram_helper/__init__.py`
- Create: `aram_helper/models.py`
- Create: `aram_helper/data_store.py`
- Create: `aram_helper/lcu_client.py`
- Create: `aram_helper/recommendations.py`
- Create: `aram_helper/app_state.py`
- Create: `aram_helper/ocr_service.py`
- Create: `aram_helper/ui.py`
- Modify: `floating_window.py`
- Modify: `hextech_ocr.py`
- Modify: `build.py`
- Modify: `LOL_ARAM_Helper.spec`
- Modify: `README.md`
- Create: `tests/test_data_store.py`
- Create: `tests/test_recommendations.py`
- Create: `tests/test_lcu_client.py`
- Create: `tests/test_app_state.py`
- Create: `tests/test_ocr_service.py`

---

## Tasks

### Task 1: Add Core Models and Data Store

**Files:**
- Create: `aram_helper/__init__.py`
- Create: `aram_helper/models.py`
- Create: `aram_helper/data_store.py`
- Create: `tests/test_data_store.py`

- [ ] **Step 1: Write data store tests**

Create `tests/test_data_store.py`:

```python
import json
import tempfile
import unittest
from pathlib import Path

from aram_helper.data_store import ChampionDataStore


class ChampionDataStoreTest(unittest.TestCase):
    def test_loads_existing_schema(self):
        payload = {
            "last_update": "2026-03-17",
            "champions": {
                "876": {
                    "name": "含羞蓓蕾 莉莉娅",
                    "tier": "T1",
                    "winrate": "59.09%",
                    "augments": ["祖母的辣椒油", "红包"],
                    "items": ["法穿鞋", "卢登"],
                }
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "champions_data.json"
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

            store = ChampionDataStore(path)
            champion = store.get_champion("876")

        self.assertEqual(champion.name, "含羞蓓蕾 莉莉娅")
        self.assertEqual(champion.tier, "T1")
        self.assertEqual(champion.augments, ("祖母的辣椒油", "红包"))

    def test_missing_champion_returns_id_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "champions_data.json"
            path.write_text('{"champions": {}}', encoding="utf-8")

            store = ChampionDataStore(path)
            champion = store.get_champion("9999")

        self.assertEqual(champion.name, "ID:9999")
        self.assertEqual(champion.augments, ())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run python -m unittest tests.test_data_store -v`

Expected: fail with `ModuleNotFoundError: No module named 'aram_helper'`.

- [ ] **Step 3: Implement models and data store**

Create `aram_helper/__init__.py`:

```python
__all__ = []
```

Create `aram_helper/models.py`:

```python
from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class ChampionRecommendation:
    champion_id: str
    name: str
    tier: str
    winrate: str
    augments: tuple[str, ...]
    items: tuple[str, ...]


class GamePhase(str, Enum):
    DISCONNECTED = "Disconnected"
    CHAMP_SELECT = "ChampSelect"
    IN_PROGRESS = "InProgress"
    OTHER = "Other"


@dataclass(frozen=True)
class ChampionSelection:
    selected_champion_id: str | None
    bench_champion_ids: tuple[str, ...]


@dataclass(frozen=True)
class AppSnapshot:
    phase: GamePhase
    status: str
    champion_ids: tuple[str, ...]
    selected_champion_id: str | None
```

Create `aram_helper/data_store.py`:

```python
import json
from pathlib import Path

from .models import ChampionRecommendation


class ChampionDataStore:
    def __init__(self, data_path: str | Path):
        self.data_path = Path(data_path)
        self._data = self._load()

    def _load(self) -> dict:
        if not self.data_path.exists():
            return {"last_update": "", "champions": {}}
        with self.data_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        data.setdefault("champions", {})
        data.setdefault("last_update", "")
        return data

    @property
    def champion_count(self) -> int:
        return len(self._data.get("champions", {}))

    def get_champion(self, champion_id: str | int) -> ChampionRecommendation:
        key = str(champion_id)
        raw = self._data.get("champions", {}).get(key, {})
        return ChampionRecommendation(
            champion_id=key,
            name=raw.get("name") or f"ID:{key}",
            tier=raw.get("tier") or "?",
            winrate=raw.get("winrate") or "?",
            augments=tuple(raw.get("augments") or ()),
            items=tuple(raw.get("items") or ()),
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run python -m unittest tests.test_data_store -v`

Expected: 2 tests pass.

- [ ] **Step 5: Commit**

```bash
git add aram_helper/__init__.py aram_helper/models.py aram_helper/data_store.py tests/test_data_store.py
git commit -m "refactor: add champion data store"
```

### Task 2: Extract LCU Client

**Files:**
- Create: `aram_helper/lcu_client.py`
- Create: `tests/test_lcu_client.py`

- [ ] **Step 1: Write LCU parsing tests**

Create `tests/test_lcu_client.py`:

```python
import unittest

from aram_helper.lcu_client import extract_lcu_credentials


class LcuClientTest(unittest.TestCase):
    def test_extracts_port_and_token(self):
        command_line = (
            '"LeagueClientUx.exe" --app-port=51521 '
            "--remoting-auth-token=abc-123_XY"
        )

        credentials = extract_lcu_credentials(command_line)

        self.assertIsNotNone(credentials)
        self.assertEqual(credentials.port, "51521")
        self.assertEqual(credentials.token, "abc-123_XY")

    def test_returns_none_when_missing_token(self):
        self.assertIsNone(extract_lcu_credentials("--app-port=51521"))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run python -m unittest tests.test_lcu_client -v`

Expected: fail with `ModuleNotFoundError` or `ImportError` for `aram_helper.lcu_client`.

- [ ] **Step 3: Implement LCU client**

Create `aram_helper/lcu_client.py`:

```python
import base64
import json
import re
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass

import psutil


@dataclass(frozen=True)
class LcuCredentials:
    port: str
    token: str


def extract_lcu_credentials(command_line: str) -> LcuCredentials | None:
    port = re.search(r"--app-port=(\d+)", command_line)
    token = re.search(r"--remoting-auth-token=([\w-]+)", command_line)
    if not port or not token:
        return None
    return LcuCredentials(port=port.group(1), token=token.group(1))


class LcuClient:
    def __init__(self):
        self.credentials: LcuCredentials | None = None

    def connect(self) -> bool:
        for proc in psutil.process_iter(["name", "cmdline"]):
            name = proc.info.get("name") or ""
            if "LeagueClientUx" not in name:
                continue
            cmdline = " ".join(proc.info.get("cmdline") or ())
            credentials = extract_lcu_credentials(cmdline)
            if credentials:
                self.credentials = credentials
                return True
        self.credentials = None
        return False

    def request(self, endpoint: str, timeout: float = 2.0):
        if not self.credentials:
            return None
        auth = base64.b64encode(f"riot:{self.credentials.token}".encode()).decode()
        url = f"https://127.0.0.1:{self.credentials.port}{endpoint}"
        request = urllib.request.Request(url, headers={"Authorization": f"Basic {auth}"})
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        try:
            with urllib.request.urlopen(request, context=context, timeout=timeout) as response:
                body = response.read().decode("utf-8")
                return json.loads(body)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            return None

    def gameflow_phase(self) -> str | None:
        return self.request("/lol-gameflow/v1/gameflow-phase")

    def champ_select_session(self) -> dict | None:
        result = self.request("/lol-champ-select/v1/session")
        return result if isinstance(result, dict) else None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run python -m unittest tests.test_lcu_client -v`

Expected: 2 tests pass.

- [ ] **Step 5: Commit**

```bash
git add aram_helper/lcu_client.py tests/test_lcu_client.py
git commit -m "refactor: extract lcu client"
```

### Task 3: Add Recommendation Engine

**Files:**
- Create: `aram_helper/recommendations.py`
- Create: `tests/test_recommendations.py`

- [ ] **Step 1: Write ranking tests**

Create `tests/test_recommendations.py`:

```python
import unittest

from aram_helper.models import ChampionRecommendation
from aram_helper.recommendations import RecommendationEngine


class RecommendationEngineTest(unittest.TestCase):
    def setUp(self):
        self.champion = ChampionRecommendation(
            champion_id="876",
            name="含羞蓓蕾 莉莉娅",
            tier="T1",
            winrate="59.09%",
            augments=("祖母的辣椒油", "红包", "咏叹奏鸣"),
            items=("法穿鞋",),
        )
        self.engine = RecommendationEngine()

    def test_exact_match_gets_rank(self):
        result = self.engine.rank_augment(self.champion, "红包")

        self.assertEqual(result.rank, 2)
        self.assertEqual(result.level, "recommended")
        self.assertEqual(result.matched_name, "红包")

    def test_unknown_gets_unknown_level(self):
        result = self.engine.rank_augment(self.champion, "不存在的强化")

        self.assertIsNone(result.rank)
        self.assertEqual(result.level, "unknown")

    def test_whitespace_is_normalized(self):
        result = self.engine.rank_augment(self.champion, "  祖母 的 辣椒油 ")

        self.assertEqual(result.rank, 1)
        self.assertEqual(result.level, "best")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run python -m unittest tests.test_recommendations -v`

Expected: fail with `ModuleNotFoundError` or missing `RecommendationEngine`.

- [ ] **Step 3: Implement recommendation engine**

Create `aram_helper/recommendations.py`:

```python
import difflib
import re
from dataclasses import dataclass

from .models import ChampionRecommendation


@dataclass(frozen=True)
class AugmentRank:
    input_name: str
    matched_name: str | None
    rank: int | None
    level: str
    score: float


def normalize_augment_name(name: str) -> str:
    return re.sub(r"\s+", "", name or "").strip().lower()


class RecommendationEngine:
    def rank_augment(self, champion: ChampionRecommendation, augment_name: str) -> AugmentRank:
        normalized_input = normalize_augment_name(augment_name)
        if not normalized_input:
            return AugmentRank(augment_name, None, None, "unknown", 0.0)

        candidates = {
            normalize_augment_name(name): name
            for name in champion.augments
            if normalize_augment_name(name)
        }
        if normalized_input in candidates:
            matched = candidates[normalized_input]
            rank = champion.augments.index(matched) + 1
            return AugmentRank(augment_name, matched, rank, self._level_for_rank(rank), 1.0)

        match = difflib.get_close_matches(normalized_input, candidates.keys(), n=1, cutoff=0.82)
        if not match:
            return AugmentRank(augment_name, None, None, "unknown", 0.0)

        matched = candidates[match[0]]
        rank = champion.augments.index(matched) + 1
        score = difflib.SequenceMatcher(None, normalized_input, match[0]).ratio()
        return AugmentRank(augment_name, matched, rank, self._level_for_rank(rank), score)

    def _level_for_rank(self, rank: int) -> str:
        if rank == 1:
            return "best"
        if rank <= 3:
            return "recommended"
        return "situational"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run python -m unittest tests.test_recommendations -v`

Expected: 3 tests pass.

- [ ] **Step 5: Commit**

```bash
git add aram_helper/recommendations.py tests/test_recommendations.py
git commit -m "refactor: add augment recommendation engine"
```

### Task 4: Add App State Service

**Files:**
- Create: `aram_helper/app_state.py`
- Create: `tests/test_app_state.py`

- [ ] **Step 1: Write state transition tests**

Create `tests/test_app_state.py`:

```python
import unittest

from aram_helper.app_state import AppStateService
from aram_helper.models import GamePhase


class FakeLcu:
    def __init__(self, connected, phase, session=None):
        self.connected = connected
        self.phase = phase
        self.session = session

    def connect(self):
        return self.connected

    def gameflow_phase(self):
        return self.phase

    def champ_select_session(self):
        return self.session


class AppStateServiceTest(unittest.TestCase):
    def test_disconnected_snapshot(self):
        service = AppStateService(FakeLcu(False, None))

        snapshot = service.poll()

        self.assertEqual(snapshot.phase, GamePhase.DISCONNECTED)
        self.assertEqual(snapshot.status, "状态: 未检测到客户端")

    def test_champ_select_snapshot(self):
        session = {
            "localPlayerCellId": 3,
            "actions": [[{"actorCellId": 3, "championId": 876}]],
            "benchChampions": [{"championId": 904}, {"championId": 63}],
        }
        service = AppStateService(FakeLcu(True, "ChampSelect", session))

        snapshot = service.poll()

        self.assertEqual(snapshot.phase, GamePhase.CHAMP_SELECT)
        self.assertEqual(snapshot.selected_champion_id, "876")
        self.assertEqual(snapshot.champion_ids, ("876", "904", "63"))

    def test_in_game_keeps_locked_champion(self):
        service = AppStateService(FakeLcu(True, "InProgress"))
        service.locked_champion_id = "876"

        snapshot = service.poll()

        self.assertEqual(snapshot.phase, GamePhase.IN_PROGRESS)
        self.assertEqual(snapshot.champion_ids, ("876",))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run python -m unittest tests.test_app_state -v`

Expected: fail with `ModuleNotFoundError` or missing `AppStateService`.

- [ ] **Step 3: Implement state service**

Create `aram_helper/app_state.py`:

```python
from .models import AppSnapshot, GamePhase


class AppStateService:
    def __init__(self, lcu_client):
        self.lcu_client = lcu_client
        self.locked_champion_id: str | None = None

    def poll(self) -> AppSnapshot:
        if not self.lcu_client.connect():
            self.locked_champion_id = None
            return AppSnapshot(GamePhase.DISCONNECTED, "状态: 未检测到客户端", (), None)

        phase = self.lcu_client.gameflow_phase()
        if phase == "ChampSelect":
            return self._champ_select_snapshot()

        if phase in {"InProgress", "GameStart"} and self.locked_champion_id:
            return AppSnapshot(
                GamePhase.IN_PROGRESS,
                "状态: 对局中",
                (self.locked_champion_id,),
                self.locked_champion_id,
            )

        return AppSnapshot(GamePhase.OTHER, "状态: 已连接", (), None)

    def _champ_select_snapshot(self) -> AppSnapshot:
        session = self.lcu_client.champ_select_session()
        if not session:
            return AppSnapshot(GamePhase.CHAMP_SELECT, "状态: 等待进入选人...", (), None)

        selected_id = self._selected_champion_id(session)
        if selected_id:
            self.locked_champion_id = selected_id

        bench_ids = tuple(
            str(item.get("championId"))
            for item in session.get("benchChampions", ())
            if item.get("championId")
        )
        champion_ids = tuple(dict.fromkeys(((selected_id,) if selected_id else ()) + bench_ids))
        status = "状态: 等待选人..." if not champion_ids else "状态: 已连接"
        return AppSnapshot(GamePhase.CHAMP_SELECT, status, champion_ids, selected_id)

    def _selected_champion_id(self, session: dict) -> str | None:
        local_cell_id = session.get("localPlayerCellId")
        for action_group in session.get("actions", ()):
            for action in action_group:
                if action.get("actorCellId") == local_cell_id and action.get("championId"):
                    return str(action["championId"])
        return None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run python -m unittest tests.test_app_state -v`

Expected: 3 tests pass.

- [ ] **Step 5: Commit**

```bash
git add aram_helper/app_state.py tests/test_app_state.py
git commit -m "refactor: add app state service"
```

### Task 5: Extract OCR Service

**Files:**
- Create: `aram_helper/ocr_service.py`
- Modify: `hextech_ocr.py`
- Create: `tests/test_ocr_service.py`

- [ ] **Step 1: Write OCR result tests**

Create `tests/test_ocr_service.py`:

```python
import unittest

from aram_helper.ocr_service import OcrRegions, parse_rapidocr_result


class OcrServiceTest(unittest.TestCase):
    def test_parse_rapidocr_result_combines_text(self):
        raw = [
            [[[0, 0], [1, 0], [1, 1], [0, 1]], "祖母的", 0.99],
            [[[0, 0], [1, 0], [1, 1], [0, 1]], "辣椒油", 0.98],
        ]

        text = parse_rapidocr_result(raw)

        self.assertEqual(text, "祖母的 辣椒油")

    def test_default_regions_has_three_slots(self):
        regions = OcrRegions.default_2k()

        self.assertEqual(len(regions.slots), 3)
        self.assertEqual(regions.slots[0]["width"], 480)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run python -m unittest tests.test_ocr_service -v`

Expected: fail with `ModuleNotFoundError` or missing `ocr_service`.

- [ ] **Step 3: Implement OCR service wrapper**

Create `aram_helper/ocr_service.py`:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class OcrRegions:
    slots: tuple[dict[str, int], dict[str, int], dict[str, int]]

    @classmethod
    def default_2k(cls):
        return cls(
            slots=(
                {"top": 810, "left": 975, "width": 480, "height": 90},
                {"top": 810, "left": 1695, "width": 480, "height": 90},
                {"top": 810, "left": 2400, "width": 480, "height": 90},
            )
        )


def parse_rapidocr_result(result) -> str:
    if not result:
        return ""
    return " ".join(str(line[1]).strip() for line in result if len(line) >= 2 and line[1]).strip()


class HextechOcrService:
    def __init__(self, regions: OcrRegions | None = None):
        import cv2
        import mss
        import numpy as np
        from rapidocr_onnxruntime import RapidOCR

        self.cv2 = cv2
        self.mss = mss
        self.np = np
        self.ocr = RapidOCR()
        self.screen = mss.mss()
        self.regions = regions or OcrRegions.default_2k()

    def recognize_augments(self) -> tuple[str, str, str]:
        return tuple(self._recognize_region(region) for region in self.regions.slots)

    def _recognize_region(self, region: dict[str, int]) -> str:
        screenshot = self.screen.grab(region)
        image = self.np.array(screenshot)
        image = self.cv2.cvtColor(image, self.cv2.COLOR_BGRA2BGR)
        result, _ = self.ocr(image)
        return parse_rapidocr_result(result)
```

Replace the screenshot and RapidOCR ownership in `hextech_ocr.py` with a thin manual debugging wrapper:

```python
#!/usr/bin/env python3
from aram_helper.data_store import ChampionDataStore
from aram_helper.ocr_service import HextechOcrService
from aram_helper.recommendations import RecommendationEngine


def main():
    champion_id = input("Champion ID: ").strip()
    store = ChampionDataStore("champions_data.json")
    champion = store.get_champion(champion_id)
    ocr = HextechOcrService()
    engine = RecommendationEngine()

    augments = ocr.recognize_augments()
    print(f"当前英雄: {champion.name}")
    for index, augment in enumerate(augments, 1):
        rank = engine.rank_augment(champion, augment)
        label = rank.rank if rank.rank is not None else "未知"
        print(f"{index}. {augment} -> {label} ({rank.level}, score={rank.score:.2f})")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run python -m unittest tests.test_ocr_service -v`

Expected: 2 tests pass.

- [ ] **Step 5: Commit**

```bash
git add aram_helper/ocr_service.py hextech_ocr.py tests/test_ocr_service.py
git commit -m "refactor: extract hextech ocr service"
```

### Task 6: Rebuild Tk UI Around Services

**Files:**
- Create: `aram_helper/ui.py`
- Modify: `floating_window.py`

- [ ] **Step 1: Create UI adapter**

Create `aram_helper/ui.py` with an `AramHelperApp` class that receives `ChampionDataStore`, `AppStateService`, `RecommendationEngine`, and optional `HextechOcrService`. The UI thread must be the only place that calls `tk.Label.config`, `pack`, `destroy`, or other Tk methods.

Use this queue pattern:

```python
import queue
import threading
import time
import tkinter as tk


class AramHelperApp:
    def __init__(self, root, data_store, state_service, recommendation_engine, ocr_service_factory):
        self.root = root
        self.data_store = data_store
        self.state_service = state_service
        self.recommendation_engine = recommendation_engine
        self.ocr_service_factory = ocr_service_factory
        self.events = queue.Queue()
        self.last_snapshot = None
        self._build_ui()

    def start(self):
        threading.Thread(target=self._poll_loop, daemon=True).start()
        self.root.after(100, self._drain_events)
        self.root.mainloop()

    def _poll_loop(self):
        while True:
            self.events.put(("snapshot", self.state_service.poll()))
            time.sleep(2)

    def _drain_events(self):
        while not self.events.empty():
            event_type, payload = self.events.get()
            if event_type == "snapshot":
                self._render_snapshot(payload)
        self.root.after(100, self._drain_events)
```

- [ ] **Step 2: Move `ChampionCard` into `aram_helper/ui.py`**

Copy the current card rendering behavior from `floating_window.py`, but make it accept a `ChampionRecommendation` dataclass instead of a dict.

```python
class ChampionCard(tk.Frame):
    def __init__(self, parent, champion, is_selected=False):
        super().__init__(parent, bg=COLORS["card_selected"] if is_selected else COLORS["card_bg"])
        self._add_name_row(champion, is_selected)
        self._add_augments(champion.augments)
        self._add_items(champion.items)
```

Keep the current colors so this task changes structure, not visual design.

- [ ] **Step 3: Convert `floating_window.py` into launcher**

Replace `floating_window.py` content with:

```python
#!/usr/bin/env python3
import os
import sys
import tkinter as tk

from aram_helper.app_state import AppStateService
from aram_helper.data_store import ChampionDataStore
from aram_helper.lcu_client import LcuClient
from aram_helper.ocr_service import HextechOcrService
from aram_helper.recommendations import RecommendationEngine
from aram_helper.ui import AramHelperApp


def resource_path(filename: str) -> str:
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


def main():
    root = tk.Tk()
    app = AramHelperApp(
        root=root,
        data_store=ChampionDataStore(resource_path("champions_data.json")),
        state_service=AppStateService(LcuClient()),
        recommendation_engine=RecommendationEngine(),
        ocr_service_factory=HextechOcrService,
    )
    app.start()


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run syntax verification**

Run: `uv run python -m py_compile floating_window.py aram_helper/ui.py`

Expected: exit code 0.

- [ ] **Step 5: Run all unit tests**

Run: `uv run python -m unittest discover -s tests -p "test_*.py" -v`

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add aram_helper/ui.py floating_window.py
git commit -m "refactor: rebuild tkinter app around services"
```

### Task 7: Move Data Update Out of UI

**Files:**
- Create: `aram_helper/data_update.py`
- Modify: `floating_window.py`
- Modify: `aram_helper/ui.py`
- Create: `tests/test_data_update.py`

- [ ] **Step 1: Write parser test**

Create `tests/test_data_update.py`:

```python
import unittest

from aram_helper.data_update import parse_champion_table


class DataUpdateTest(unittest.TestCase):
    def test_parse_champion_table(self):
        html = """
        <table><tbody>
        <tr>
          <td>1</td>
          <td><a href="/zh-CN/champion-stats/876">含羞蓓蕾 莉莉娅攻略</a></td>
          <td><span>T1</span></td>
          <td><span>59.09%</span></td>
          <td></td>
          <td><a><img alt="祖母的辣椒油"></a><a><img alt="红包"></a></td>
        </tr>
        </tbody></table>
        """

        champions = parse_champion_table(html)

        self.assertEqual(champions["876"]["name"], "含羞蓓蕾 莉莉娅")
        self.assertEqual(champions["876"]["tier"], "T1")
        self.assertEqual(champions["876"]["augments"], ["祖母的辣椒油", "红包"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run python -m unittest tests.test_data_update -v`

Expected: fail with missing `aram_helper.data_update`.

- [ ] **Step 3: Implement parser with standard library HTML parser**

Create `aram_helper/data_update.py`:

```python
import re
from html.parser import HTMLParser


class ChampionTableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.current_row = None
        self.current_cell = None
        self.capture_text = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "tr":
            self.current_row = []
        elif tag == "td" and self.current_row is not None:
            self.current_cell = {"text": "", "links": [], "alts": []}
        elif tag == "a" and self.current_cell is not None:
            self.current_cell["links"].append(attrs.get("href", ""))
            self.capture_text = True
        elif tag == "img" and self.current_cell is not None:
            alt = attrs.get("alt")
            if alt:
                self.current_cell["alts"].append(alt)

    def handle_endtag(self, tag):
        if tag == "td" and self.current_row is not None and self.current_cell is not None:
            self.current_row.append(self.current_cell)
            self.current_cell = None
        elif tag == "tr" and self.current_row is not None:
            self.rows.append(self.current_row)
            self.current_row = None
        elif tag == "a":
            self.capture_text = False

    def handle_data(self, data):
        if self.current_cell is not None:
            self.current_cell["text"] += data


def parse_champion_table(html: str) -> dict:
    parser = ChampionTableParser()
    parser.feed(html)
    champions = {}
    for row in parser.rows:
        if len(row) < 6:
            continue
        link_text = " ".join(row[1]["links"])
        match = re.search(r"champion-stats/(\d+)", link_text)
        if not match:
            continue
        champion_id = match.group(1)
        name = row[1]["text"].strip().replace("攻略", "").strip()
        tier_match = re.search(r"T\d", row[2]["text"])
        winrate_match = re.search(r"\d+\.\d+%", row[3]["text"])
        champions[champion_id] = {
            "name": name,
            "tier": tier_match.group(0) if tier_match else "?",
            "winrate": winrate_match.group(0) if winrate_match else "?",
            "augments": row[5]["alts"],
        }
    return champions
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run python -m unittest tests.test_data_update -v`

Expected: 1 test passes.

- [ ] **Step 5: Wire UI update button to data update service**

In `aram_helper/data_update.py`, add a callable updater result:

```python
from dataclasses import dataclass
from datetime import datetime
import json
import ssl
import urllib.request


@dataclass(frozen=True)
class DataUpdateResult:
    ok: bool
    message: str
    champion_count: int


def fetch_url(url: str, timeout: float = 30.0) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
    )
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
        return response.read().decode("utf-8")


def update_champion_data(data_path: str, source_url: str) -> DataUpdateResult:
    html = fetch_url(source_url)
    champions = parse_champion_table(html)
    if not champions:
        return DataUpdateResult(False, "未解析到英雄数据", 0)
    payload = {
        "last_update": datetime.now().strftime("%Y-%m-%d"),
        "champions": champions,
    }
    with open(data_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    return DataUpdateResult(True, "更新成功", len(champions))
```

In `aram_helper/ui.py`, replace direct scraping in the button handler with a worker that posts back to the Tk event queue:

```python
def on_update_clicked(self):
    self.update_btn.config(state="disabled", text="更新中...")
    threading.Thread(target=self._update_data_worker, daemon=True).start()


def _update_data_worker(self):
    result = self.update_data()
    self.events.put(("data_updated", result))


def _handle_data_updated(self, result):
    if result.ok:
        self.data_store.reload()
        self.update_btn.config(text="更新成功", bg="#10b981")
    else:
        self.update_btn.config(text="更新失败", bg="#ef4444")
    self.root.after(
        2000,
        lambda: self.update_btn.config(
            state="normal",
            text="更新数据",
            bg=COLORS["card_selected"],
        ),
    )
```

Also add `ChampionDataStore.reload()`:

```python
def reload(self):
    self._data = self._load()
```

- [ ] **Step 6: Run all unit tests and syntax checks**

Run: `uv run python -m unittest discover -s tests -p "test_*.py" -v`

Expected: all tests pass.

Run: `uv run python -m py_compile floating_window.py aram_helper/*.py`

Expected: exit code 0.

- [ ] **Step 7: Commit**

```bash
git add aram_helper/data_update.py aram_helper/ui.py floating_window.py tests/test_data_update.py
git commit -m "refactor: move data update out of ui"
```

### Task 8: Clean Build and Runtime Packaging

**Files:**
- Modify: `requirements.txt`
- Modify: `build.py`
- Modify: `LOL_ARAM_Helper.spec`
- Modify: `README.md`

- [ ] **Step 1: Remove invalid build data entry**

Modify `build.py` so it does not reference missing root-level `scraper.py`:

```python
PyInstaller.__main__.run([
    "floating_window.py",
    "--name=LOL_ARAM_Helper",
    "--onefile",
    "--windowed",
    "--add-data=champions_data.json;.",
    "--hidden-import=psutil",
    "--hidden-import=rapidocr_onnxruntime",
    "--hidden-import=mss",
    "--hidden-import=cv2",
    "--hidden-import=numpy",
    "--clean",
])
```

- [ ] **Step 2: Update spec hidden imports**

Modify `LOL_ARAM_Helper.spec`:

```python
hiddenimports=[
    "psutil",
    "rapidocr_onnxruntime",
    "mss",
    "cv2",
    "numpy",
],
```

- [ ] **Step 3: Update README run commands**

Replace the development commands with:

```bash
uv pip install -r requirements.txt
uv run python floating_window.py
uv run python -m unittest discover -s tests -p "test_*.py" -v
uv run python build.py
```

- [ ] **Step 4: Run verification**

Run: `uv run python -m unittest discover -s tests -p "test_*.py" -v`

Expected: all tests pass.

Run: `uv run python -m py_compile floating_window.py hextech_ocr.py aram_helper/*.py`

Expected: exit code 0.

- [ ] **Step 5: Commit**

```bash
git add requirements.txt build.py LOL_ARAM_Helper.spec README.md
git commit -m "chore: update build configuration"
```

### Task 9: Manual Runtime Verification

**Files:**
- No source files required.

- [ ] **Step 1: Start app without LOL client**

Run: `uv run python floating_window.py`

Expected UI: status text shows `状态: 未检测到客户端`; no exception in terminal.

- [ ] **Step 2: Start app with LOL client in champ select**

Run: `uv run python floating_window.py`

Expected UI: selected champion card appears first, bench champions appear below, selected card has highlighted border.

- [ ] **Step 3: Verify in-game OCR path**

Enter a game, open an augment selection, press the app's scan button.

Expected UI: three OCR result rows appear. Exact matches show rank; unmatched OCR text shows unknown without crashing.

- [ ] **Step 4: Commit verification notes if docs were changed**

If README gained manual QA notes:

```bash
git add README.md
git commit -m "docs: add runtime verification notes"
```

---

## Execution Notes

- The current worktree already has uncommitted changes to `floating_window.py`, `requirements.txt`, and untracked `hextech_ocr.py`. Treat those as user work and preserve them during implementation.
- Do not delete the `lib/` or nested Web/Node prototype directories in this refactor. After the app is stable, archive cleanup can be a separate task.
- The existing data only ranks the currently stored ordered augment list. To rank more than the top 3, the data update step must collect a longer ordered augment list from the source page.
- Avoid direct Tk calls outside the main thread. Background workers communicate through a queue, and `root.after()` drains events.

## Self-Review

- Spec coverage: champ select display is covered by Tasks 1, 4, and 6; in-game augment ranking is covered by Tasks 3, 5, and 6; data update and packaging are covered by Tasks 7 and 8.
- Placeholder scan: no open placeholder markers are required for implementation.
- Type consistency: `ChampionRecommendation`, `AppSnapshot`, `GamePhase`, and `AugmentRank` are introduced before use in later tasks.
