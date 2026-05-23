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
