import json
import tempfile
import unittest
from pathlib import Path

from aram_helper.data_update import (
    parse_augment_catalog,
    parse_champion_detail_augments,
    parse_champion_table,
    update_champion_data,
)


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
            pages = {
                "https://example.test/zh-CN": html,
                "https://example.test/zh-CN/augments": """
                    <a href="/zh-CN/augments/1045"><img alt="炼狱导管"></a>
                """,
                "https://example.test/zh-CN/champion-stats/876": """
                    <script>self.__next_f.push([1,"{\\"augments\\":{\\"1045\\":{\\"tier\\":\\"1\\",\\"num_win_games\\":\\"64\\",\\"win_rate\\":\\"0.64\\",\\"num_games\\":\\"100\\",\\"pick_rate\\":\\"0.10\\"}}}"])</script>
                """,
            }

            result = update_champion_data(
                path,
                "https://example.test/zh-CN",
                fetcher=lambda url: pages[url],
                max_workers=1,
            )
            saved = json.loads(path.read_text(encoding="utf-8"))

        self.assertTrue(result.ok)
        self.assertEqual(result.champion_count, 1)
        self.assertEqual(saved["champions"]["876"]["items"], ["法穿鞋", "卢登"])
        self.assertEqual(saved["champions"]["876"]["augments"], ["炼狱导管"])

    def test_parse_augment_catalog_maps_ids_to_names(self):
        html = """
        <a class="block" href="/zh-CN/augments/1045">
          <div><img src="/x.png" alt="炼狱导管"/></div>
        </a>
        <a class="block" href="/zh-CN/augments/1390">
          <div><img src="/x.png" alt="超凡邪恶"/></div>
        </a>
        <a class="block" href="/zh-CN/augments/1009">
          <div aria-hidden="true"></div>
          <p>霸符兄弟</p>
        </a>
        """

        catalog = parse_augment_catalog(html)

        self.assertEqual(catalog["1045"], "炼狱导管")
        self.assertEqual(catalog["1390"], "超凡邪恶")
        self.assertEqual(catalog["1009"], "霸符兄弟")

    def test_parse_champion_detail_augments_sorts_by_tier_then_winrate(self):
        html = """
        <script>self.__next_f.push([1,"{\\"augments\\":{
          \\"1390\\":{\\"tier\\":\\"1\\",\\"num_win_games\\":\\"62\\",\\"win_rate\\":\\"0.62\\",\\"num_games\\":\\"100\\",\\"pick_rate\\":\\"0.10\\"},
          \\"1045\\":{\\"tier\\":\\"1\\",\\"num_win_games\\":\\"64\\",\\"win_rate\\":\\"0.64\\",\\"num_games\\":\\"100\\",\\"pick_rate\\":\\"0.10\\"},
          \\"1238\\":{\\"tier\\":\\"2\\",\\"num_win_games\\":\\"90\\",\\"win_rate\\":\\"0.90\\",\\"num_games\\":\\"100\\",\\"pick_rate\\":\\"0.10\\"}
        }}"])</script>
        """

        augments = parse_champion_detail_augments(
            html,
            {
                "1045": "炼狱导管",
                "1390": "超凡邪恶",
                "1238": "质变：棱彩阶",
            },
        )

        self.assertEqual(augments, ["炼狱导管", "超凡邪恶", "质变：棱彩阶"])


if __name__ == "__main__":
    unittest.main()
