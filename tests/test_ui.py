import unittest

from aram_helper.models import ChampionRecommendation
from aram_helper.recommendations import AugmentRank, RecommendationEngine
from aram_helper.ui import (
    build_overlay_title,
    build_rank_rows,
    format_card_augments,
    format_rank_line,
    rank_style,
)


class UiFormattingTest(unittest.TestCase):
    def test_best_rank_uses_star_and_rank(self):
        rank = AugmentRank("红包", "红包", 1, "best", 1.0, total=10, quintile=1, quintile_label="前20%")

        text = format_rank_line(1, "红包", rank)

        self.assertEqual(text, "★ 1. 红包  总排 #1/10 · 前20%")

    def test_unknown_rank_does_not_show_rank_number(self):
        rank = AugmentRank("未知", None, None, "unknown", 0.0)

        text = format_rank_line(2, "未知", rank)

        self.assertEqual(text, "○ 2. 未知  未收录")

    def test_rank_style_for_recommended(self):
        style = rank_style("recommended")

        self.assertEqual(style["prefix"], "●")
        self.assertEqual(style["color"], "#00FF00")

    def test_build_rank_rows_for_overlay(self):
        champion = ChampionRecommendation(
            champion_id="876",
            name="含羞蓓蕾 莉莉娅",
            tier="T1",
            winrate="59.09%",
            augments=("祖母的辣椒油", "红包"),
            items=(),
        )

        rows = build_rank_rows(champion, ("红包", "未知"), RecommendationEngine())

        self.assertEqual(rows[0]["text"], "● 1. 红包  总排 #2/2 · 前60%")
        self.assertEqual(rows[0]["color"], "#38BDF8")
        self.assertEqual(rows[1]["color"], "#FF6666")

    def test_overlay_title_includes_scan_number(self):
        champion = ChampionRecommendation(
            champion_id="157",
            name="疾风剑豪 亚索",
            tier="T2",
            winrate="51.54%",
            augments=(),
            items=(),
        )

        title = build_overlay_title(champion, 2)

        self.assertEqual(title, "疾风剑豪 亚索 海克斯推荐 #2 (F6)")

    def test_card_augment_summary_limits_full_detail_list(self):
        text = format_card_augments(("炼狱导管", "超凡邪恶", "质变：棱彩阶", "祖母的辣椒油"))

        self.assertEqual(text, "炼狱导管 / 超凡邪恶 / 质变：棱彩阶 / 等 4 个")


if __name__ == "__main__":
    unittest.main()
