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

        if phase in {"InProgress", "GameStart"}:
            champion_id = self.locked_champion_id or self._in_game_champion_id()
            if champion_id:
                self.locked_champion_id = champion_id
                return AppSnapshot(
                    GamePhase.IN_PROGRESS,
                    "状态: 对局中",
                    (champion_id,),
                    champion_id,
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

    def _in_game_champion_id(self) -> str | None:
        gameflow_session = self.lcu_client.gameflow_session()
        if not gameflow_session:
            return None

        selections = gameflow_session.get("gameData", {}).get("playerChampionSelections", ())
        for selection in selections:
            champion_id = selection.get("championId")
            if champion_id:
                return str(champion_id)
        return None
