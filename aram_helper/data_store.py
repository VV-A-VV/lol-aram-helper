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

    def reload(self):
        self._data = self._load()

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
