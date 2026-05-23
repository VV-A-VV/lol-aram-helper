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
    total: int = 0
    quintile: int | None = None
    quintile_label: str = "未收录"


def normalize_augment_name(name: str) -> str:
    return re.sub(r"\s+", "", name or "").strip().lower()


def quintile_for_rank(rank: int, total: int) -> int:
    if rank <= 0 or total <= 0:
        return 5
    if rank >= total and total >= 5:
        return 5
    return min(5, max(1, int((rank - 1) * 5 / total) + 1))


def quintile_label(quintile: int | None) -> str:
    labels = {
        1: "前20%",
        2: "前40%",
        3: "前60%",
        4: "前80%",
        5: "后20%",
    }
    return labels.get(quintile, "未收录")


class RecommendationEngine:
    def rank_augment(self, champion: ChampionRecommendation, augment_name: str) -> AugmentRank:
        normalized_input = normalize_augment_name(augment_name)
        total = len(champion.augments)
        if not normalized_input:
            return AugmentRank(augment_name, None, None, "unknown", 0.0, total=total)

        candidates = {
            normalize_augment_name(name): name
            for name in champion.augments
            if normalize_augment_name(name)
        }
        if normalized_input in candidates:
            matched = candidates[normalized_input]
            rank = champion.augments.index(matched) + 1
            quintile = quintile_for_rank(rank, total)
            return AugmentRank(
                augment_name,
                matched,
                rank,
                self._level_for_rank(rank),
                1.0,
                total=total,
                quintile=quintile,
                quintile_label=quintile_label(quintile),
            )

        match = difflib.get_close_matches(normalized_input, candidates.keys(), n=1, cutoff=0.82)
        if not match:
            return AugmentRank(augment_name, None, None, "unknown", 0.0, total=total)

        matched = candidates[match[0]]
        rank = champion.augments.index(matched) + 1
        score = difflib.SequenceMatcher(None, normalized_input, match[0]).ratio()
        quintile = quintile_for_rank(rank, total)
        return AugmentRank(
            augment_name,
            matched,
            rank,
            self._level_for_rank(rank),
            score,
            total=total,
            quintile=quintile,
            quintile_label=quintile_label(quintile),
        )

    def _level_for_rank(self, rank: int) -> str:
        if rank == 1:
            return "best"
        if rank <= 3:
            return "recommended"
        return "situational"
