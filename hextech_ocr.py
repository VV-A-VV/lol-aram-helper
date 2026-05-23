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
