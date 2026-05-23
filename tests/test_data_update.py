import json
import tempfile
import unittest
from pathlib import Path

from aram_helper.data_update import parse_champion_table, update_champion_data


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
        self.assertEqual(champions["876"]["winrate"], "59.09%")
        self.assertEqual(champions["876"]["augments"], ["祖母的辣椒油", "红包"])

    def test_update_preserves_existing_items(self):
        html = """
        <table><tbody>
        <tr>
          <td>1</td>
          <td><a href="/zh-CN/champion-stats/876">含羞蓓蕾 莉莉娅攻略</a></td>
          <td>T1</td>
          <td>59.09%</td>
          <td></td>
          <td><a><img alt="祖母的辣椒油"></a></td>
        </tr>
        </tbody></table>
        """
        existing = {
            "champions": {
                "876": {
                    "name": "含羞蓓蕾 莉莉娅",
                    "tier": "T2",
                    "winrate": "50.00%",
                    "augments": [],
                    "items": ["法穿鞋", "卢登"],
                }
            }
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "champions_data.json"
            path.write_text(json.dumps(existing, ensure_ascii=False), encoding="utf-8")

            result = update_champion_data(path, "https://example.test", fetcher=lambda _url: html)
            saved = json.loads(path.read_text(encoding="utf-8"))

        self.assertTrue(result.ok)
        self.assertEqual(result.champion_count, 1)
        self.assertEqual(saved["champions"]["876"]["items"], ["法穿鞋", "卢登"])


if __name__ == "__main__":
    unittest.main()
