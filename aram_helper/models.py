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
