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
        self.assertEqual(result.total, 3)
        self.assertEqual(result.quintile, 2)
        self.assertEqual(result.quintile_label, "前40%")
        self.assertEqual(result.level, "recommended")
        self.assertEqual(result.matched_name, "红包")

    def test_unknown_gets_unknown_level(self):
        result = self.engine.rank_augment(self.champion, "不存在的强化")

        self.assertIsNone(result.rank)
        self.assertEqual(result.total, 3)
        self.assertIsNone(result.quintile)
        self.assertEqual(result.quintile_label, "未收录")
        self.assertEqual(result.level, "unknown")

    def test_whitespace_is_normalized(self):
        result = self.engine.rank_augment(self.champion, "  祖母 的 辣椒油 ")

        self.assertEqual(result.rank, 1)
        self.assertEqual(result.level, "best")

    def test_quintile_uses_total_recommendation_count(self):
        champion = ChampionRecommendation(
            champion_id="1",
            name="测试英雄",
            tier="T1",
            winrate="50.00%",
            augments=tuple(f"海克斯{i}" for i in range(1, 11)),
            items=(),
        )

        first = self.engine.rank_augment(champion, "海克斯1")
        fourth = self.engine.rank_augment(champion, "海克斯4")
        ninth = self.engine.rank_augment(champion, "海克斯9")

        self.assertEqual(first.quintile_label, "前20%")
        self.assertEqual(fourth.quintile_label, "前40%")
        self.assertEqual(ninth.quintile_label, "后20%")


if __name__ == "__main__":
    unittest.main()
